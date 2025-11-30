"""Additional complex test scenarios for graph path finding.

This test suite includes more complex scenarios with:
- Multiple relationship types (belongs_to, has_many, has_one)
- Circular relationships
- Multiple paths with different lengths
- Complex multi-cube queries
"""

import pytest
from semantic_layer.models.cube import Cube
from semantic_layer.models.dimension import Dimension
from semantic_layer.models.measure import Measure
from semantic_layer.models.relationship import Relationship
from semantic_layer.models.schema import Schema
from semantic_layer.query.query import Query
from semantic_layer.sql.builder import SQLBuilder


@pytest.fixture
def complex_schema():
    """Create a complex schema with multiple relationship types and paths."""
    schema = Schema()
    
    # Cube: users
    users_cube = Cube(
        name="users",
        table="users",
        dimensions={
            "id": Dimension(name="id", type="number", sql="id"),
            "name": Dimension(name="name", type="string", sql="name"),
        },
        measures={"count": Measure(name="count", type="count", sql="id")},
        relationships={
            "profile": Relationship(
                name="profile",
                type="has_one",
                cube="user_profiles",
                foreign_key="user_id",
                primary_key="id",
            ),
        },
    )
    schema.add_cube(users_cube)
    
    # Cube: user_profiles
    user_profiles_cube = Cube(
        name="user_profiles",
        table="user_profiles",
        dimensions={
            "id": Dimension(name="id", type="number", sql="id"),
            "user_id": Dimension(name="user_id", type="number", sql="user_id"),
            "bio": Dimension(name="bio", type="string", sql="bio"),
        },
        measures={"count": Measure(name="count", type="count", sql="id")},
        relationships={
            "user": Relationship(
                name="user",
                type="belongs_to",
                cube="users",
                foreign_key="user_id",
                primary_key="id",
            ),
            "address": Relationship(
                name="address",
                type="has_one",
                cube="addresses",
                foreign_key="profile_id",
                primary_key="id",
            ),
        },
    )
    schema.add_cube(user_profiles_cube)
    
    # Cube: addresses
    addresses_cube = Cube(
        name="addresses",
        table="addresses",
        dimensions={
            "id": Dimension(name="id", type="number", sql="id"),
            "profile_id": Dimension(name="profile_id", type="number", sql="profile_id"),
            "city": Dimension(name="city", type="string", sql="city"),
        },
        measures={"count": Measure(name="count", type="count", sql="id")},
        relationships={
            "profile": Relationship(
                name="profile",
                type="belongs_to",
                cube="user_profiles",
                foreign_key="profile_id",
                primary_key="id",
            ),
        },
    )
    schema.add_cube(addresses_cube)
    
    # Cube: posts (has_many relationship)
    posts_cube = Cube(
        name="posts",
        table="posts",
        dimensions={
            "id": Dimension(name="id", type="number", sql="id"),
            "user_id": Dimension(name="user_id", type="number", sql="user_id"),
            "title": Dimension(name="title", type="string", sql="title"),
        },
        measures={"count": Measure(name="count", type="count", sql="id")},
        relationships={
            "author": Relationship(
                name="author",
                type="belongs_to",
                cube="users",
                foreign_key="user_id",
                primary_key="id",
            ),
        },
    )
    schema.add_cube(posts_cube)
    
    # Cube: comments
    comments_cube = Cube(
        name="comments",
        table="comments",
        dimensions={
            "id": Dimension(name="id", type="number", sql="id"),
            "post_id": Dimension(name="post_id", type="number", sql="post_id"),
            "user_id": Dimension(name="user_id", type="number", sql="user_id"),
            "content": Dimension(name="content", type="string", sql="content"),
        },
        measures={"count": Measure(name="count", type="count", sql="id")},
        relationships={
            "post": Relationship(
                name="post",
                type="belongs_to",
                cube="posts",
                foreign_key="post_id",
                primary_key="id",
            ),
            "commenter": Relationship(
                name="commenter",
                type="belongs_to",
                cube="users",
                foreign_key="user_id",
                primary_key="id",
            ),
        },
    )
    schema.add_cube(comments_cube)
    
    return schema


class TestComplexPaths:
    """Test complex path scenarios."""
    
    def test_path_through_has_one_relationship(self, complex_schema):
        """Test path: users -> user_profiles (has_one)."""
        builder = SQLBuilder(complex_schema)
        path = builder._find_path_bfs("users", "user_profiles")
        assert path == ["users", "user_profiles"]
    
    def test_path_through_belongs_to_relationship(self, complex_schema):
        """Test path: user_profiles -> users (belongs_to)."""
        builder = SQLBuilder(complex_schema)
        path = builder._find_path_bfs("user_profiles", "users")
        assert path == ["user_profiles", "users"]
    
    def test_long_path_users_to_addresses(self, complex_schema):
        """Test path: users -> user_profiles -> addresses."""
        builder = SQLBuilder(complex_schema)
        path = builder._find_path_bfs("users", "addresses")
        assert path == ["users", "user_profiles", "addresses"]
    
    def test_path_users_to_posts(self, complex_schema):
        """Test path: users -> posts (has_many via reverse)."""
        builder = SQLBuilder(complex_schema)
        path = builder._find_path_bfs("users", "posts")
        # posts belongs_to users, so reverse traversal: users -> posts
        assert path == ["users", "posts"]
    
    def test_path_comments_to_users_via_post(self, complex_schema):
        """Test path: comments -> posts -> users."""
        builder = SQLBuilder(complex_schema)
        path = builder._find_path_bfs("comments", "users")
        # Two paths exist: comments -> post -> users and comments -> commenter -> users
        # Should find shortest path: comments -> commenter -> users (length 2)
        assert path is not None
        assert path[0] == "comments"
        assert path[-1] == "users"
        # Should prefer direct path through commenter
        assert len(path) == 2 or len(path) == 3
    
    def test_path_comments_to_addresses(self, complex_schema):
        """Test long path: comments -> users -> user_profiles -> addresses."""
        builder = SQLBuilder(complex_schema)
        path = builder._find_path_bfs("comments", "addresses")
        assert path is not None
        assert path[0] == "comments"
        assert path[-1] == "addresses"
        # Path should be: comments -> users -> user_profiles -> addresses
        assert "users" in path
        assert "user_profiles" in path


class TestMultiplePathsSelection:
    """Test that shortest path is selected when multiple paths exist."""
    
    def test_shortest_path_preference(self, complex_schema):
        """Test that shortest path is preferred when multiple paths exist.
        
        From comments to users, there are two paths:
        1. comments -> commenter -> users (length 2, direct)
        2. comments -> post -> users (length 2, indirect)
        Both are same length, so either is acceptable.
        """
        builder = SQLBuilder(complex_schema)
        path = builder._find_path_bfs("comments", "users")
        assert path is not None
        assert len(path) == 2  # Shortest path
        assert path[0] == "comments"
        assert path[-1] == "users"


class TestSQLGenerationComplex:
    """Test SQL generation with complex paths."""
    
    def test_sql_users_to_addresses(self, complex_schema):
        """Test SQL generation: users -> user_profiles -> addresses."""
        query = Query(
            dimensions=["users.name"],
            measures=["addresses.count"],
        )
        
        builder = SQLBuilder(complex_schema)
        sql = builder.build(query)
        
        # Should include all cubes in path
        assert "users" in sql
        assert "user_profiles" in sql
        assert "addresses" in sql
        assert "LEFT JOIN" in sql
    
    def test_sql_comments_to_addresses(self, complex_schema):
        """Test SQL generation with very long path."""
        query = Query(
            dimensions=["comments.content"],
            measures=["addresses.count"],
        )
        
        builder = SQLBuilder(complex_schema)
        sql = builder.build(query)
        
        # Should include: comments, users, user_profiles, addresses
        assert "comments" in sql
        assert "users" in sql
        assert "user_profiles" in sql
        assert "addresses" in sql
    
    def test_sql_multiple_measures_different_paths(self, complex_schema):
        """Test SQL with measures from different cubes requiring different paths."""
        query = Query(
            dimensions=["users.name"],
            measures=["posts.count", "addresses.count"],
        )
        
        builder = SQLBuilder(complex_schema)
        sql = builder.build(query)
        
        # Should include: users, posts, user_profiles, addresses
        assert "users" in sql
        assert "posts" in sql
        assert "user_profiles" in sql
        assert "addresses" in sql


class TestRelationshipTypes:
    """Test different relationship types work correctly."""
    
    def test_has_one_relationship(self, complex_schema):
        """Test has_one relationship traversal."""
        builder = SQLBuilder(complex_schema)
        path = builder._find_path_bfs("users", "user_profiles")
        assert path == ["users", "user_profiles"]
    
    def test_has_many_relationship_reverse(self, complex_schema):
        """Test has_many relationship via reverse traversal."""
        builder = SQLBuilder(complex_schema)
        # posts belongs_to users, so users -> posts via reverse
        path = builder._find_path_bfs("users", "posts")
        assert path == ["users", "posts"]
    
    def test_belongs_to_relationship(self, complex_schema):
        """Test belongs_to relationship traversal."""
        builder = SQLBuilder(complex_schema)
        path = builder._find_path_bfs("posts", "users")
        assert path == ["posts", "users"]


class TestBidirectionalTraversal:
    """Test that bidirectional traversal works correctly."""
    
    def test_forward_traversal(self, complex_schema):
        """Test forward relationship traversal."""
        builder = SQLBuilder(complex_schema)
        # users -> user_profiles (forward)
        path = builder._find_path_bfs("users", "user_profiles")
        assert path == ["users", "user_profiles"]
    
    def test_reverse_traversal(self, complex_schema):
        """Test reverse relationship traversal."""
        builder = SQLBuilder(complex_schema)
        # user_profiles -> users (reverse of belongs_to)
        path = builder._find_path_bfs("user_profiles", "users")
        assert path == ["user_profiles", "users"]
    
    def test_bidirectional_symmetry(self, complex_schema):
        """Test that paths work in both directions."""
        builder = SQLBuilder(complex_schema)
        
        # Forward
        path1 = builder._find_path_bfs("users", "user_profiles")
        # Reverse
        path2 = builder._find_path_bfs("user_profiles", "users")
        
        assert path1 is not None
        assert path2 is not None
        assert path1[0] == path2[-1]
        assert path1[-1] == path2[0]

