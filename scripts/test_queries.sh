#!/bin/bash

# Test queries script for SemanticQuark

API_URL="http://localhost:8000"

echo "🧪 Testing SemanticQuark API..."
echo ""

# Test 1: Health check
echo "1️⃣ Testing health endpoint..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" -eq 200 ]; then
    echo "✅ Health check passed"
    echo "   Response: $body"
else
    echo "❌ Health check failed (HTTP $http_code)"
fi
echo ""

# Test 2: Schema endpoint
echo "2️⃣ Testing schema endpoint..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/v1/schema")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" -eq 200 ]; then
    echo "✅ Schema endpoint passed"
    echo "   Response: $body" | python3 -m json.tool 2>/dev/null || echo "   Response: $body"
else
    echo "❌ Schema endpoint failed (HTTP $http_code)"
fi
echo ""

# Test 3: Simple query - count orders
echo "3️⃣ Testing query - count orders..."
query='{"measures": ["orders.count"]}'
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/v1/query" \
    -H "Content-Type: application/json" \
    -d "$query")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" -eq 200 ]; then
    echo "✅ Query passed"
    echo "   Response: $body" | python3 -m json.tool 2>/dev/null || echo "   Response: $body"
else
    echo "❌ Query failed (HTTP $http_code)"
    echo "   Response: $body"
fi
echo ""

# Test 4: Query with dimensions
echo "4️⃣ Testing query - orders by status..."
query='{"dimensions": ["orders.status"], "measures": ["orders.count", "orders.total_revenue"]}'
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/v1/query" \
    -H "Content-Type: application/json" \
    -d "$query")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" -eq 200 ]; then
    echo "✅ Query with dimensions passed"
    echo "   Response: $body" | python3 -m json.tool 2>/dev/null || echo "   Response: $body"
else
    echo "❌ Query with dimensions failed (HTTP $http_code)"
    echo "   Response: $body"
fi
echo ""

# Test 5: Query with filters
echo "5️⃣ Testing query - filtered orders..."
query='{"dimensions": ["orders.status"], "measures": ["orders.count"], "filters": [{"dimension": "orders.status", "operator": "equals", "values": ["completed"]}]}'
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/v1/query" \
    -H "Content-Type: application/json" \
    -d "$query")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" -eq 200 ]; then
    echo "✅ Query with filters passed"
    echo "   Response: $body" | python3 -m json.tool 2>/dev/null || echo "   Response: $body"
else
    echo "❌ Query with filters failed (HTTP $http_code)"
    echo "   Response: $body"
fi
echo ""

# Test 6: Query logs
echo "6️⃣ Testing query logs endpoint..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/v1/logs?limit=5")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" -eq 200 ]; then
    echo "✅ Query logs endpoint passed"
    echo "   Response: $body" | python3 -m json.tool 2>/dev/null || echo "   Response: $body"
else
    echo "❌ Query logs endpoint failed (HTTP $http_code)"
fi
echo ""

# Test 7: Metrics endpoint
echo "7️⃣ Testing metrics endpoint..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/v1/metrics")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" -eq 200 ]; then
    echo "✅ Metrics endpoint passed"
    echo "   Response: $body" | python3 -m json.tool 2>/dev/null || echo "   Response: $body"
else
    echo "❌ Metrics endpoint failed (HTTP $http_code)"
fi
echo ""

# Test 8: Pre-aggregations endpoint
echo "8️⃣ Testing pre-aggregations endpoint..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/v1/pre-aggregations")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" -eq 200 ]; then
    echo "✅ Pre-aggregations endpoint passed"
    echo "   Response: $body" | python3 -m json.tool 2>/dev/null || echo "   Response: $body"
else
    echo "⚠️  Pre-aggregations endpoint returned HTTP $http_code (may not be configured)"
fi
echo ""

echo "🎉 Testing complete!"

