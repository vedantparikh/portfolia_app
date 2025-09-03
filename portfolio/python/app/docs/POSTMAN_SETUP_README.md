# 🚀 Portfolia API - Postman Collection Setup Guide

This guide will help you set up and use the comprehensive Postman collection for the Portfolia API with automatic authentication token sharing.

## 📥 **Import the Collection**

1. **Download the collection file**: `Portfolia_API.postman_collection.json`
2. **Open Postman** and click **"Import"**
3. **Drag and drop** the JSON file or click **"Upload Files"**
4. **Import** the collection

## 🔧 **Initial Setup**

### **1. Configure Environment Variables**

The collection uses several variables that are automatically managed:

- **`base_url`**: Your API base URL (default: `http://127.0.0.1:8000`)
- **`auth_token`**: JWT authentication token (automatically set after login)
- **`user_id`**: Current user ID (automatically set after registration)
- **`portfolio_id`**: Portfolio ID (automatically set after portfolio creation)
- **`asset_id`**: Asset ID (automatically set after asset creation)
- **`transaction_id`**: Transaction ID (automatically set after transaction creation)

### **2. Update Base URL (if needed)**

If your API is running on a different port or host:

1. Click on the collection name **"Portfolia API"**
2. Go to **"Variables"** tab
3. Update the **`base_url`** value
4. Click **"Save"**

## 🔐 **Authentication Flow**

### **Step 1: Register a User**

1. **Run "Register User"** request
2. The response will automatically set your `user_id`
3. **Status**: 201 Created

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

### **Step 2: Login to Get Token**

1. **Run "Login User"** request
2. The response will automatically set your `auth_token`
3. **Status**: 200 OK

**Request Body:**
```json
{
  "username": "testuser",
  "password": "SecurePass123!"
}
```

### **Step 3: Token is Automatically Shared**

✅ **All subsequent requests will automatically include the authentication token!**

The collection is configured with **Bearer Token authentication** at the collection level, so every request automatically includes:
```
Authorization: Bearer {{auth_token}}
```

## 📊 **API Endpoints Overview**

### **🔐 Authentication**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - User logout

### **📊 Portfolios**
- `POST /api/v1/portfolios` - Create portfolio
- `GET /api/v1/portfolios` - Get user portfolios
- `GET /api/v1/portfolios/{id}` - Get specific portfolio
- `PUT /api/v1/portfolios/{id}` - Update portfolio
- `DELETE /api/v1/portfolios/{id}` - Delete portfolio
- `GET /api/v1/portfolios/{id}/summary` - Portfolio summary

### **💎 Assets**
- `POST /api/v1/assets` - Create financial asset
- `GET /api/v1/assets` - Get assets with filtering
- `GET /api/v1/assets/{id}` - Get specific asset
- `PUT /api/v1/assets/{id}` - Update asset
- `DELETE /api/v1/assets/{id}` - Delete asset
- `GET /api/v1/assets/search/{query}` - Search assets
- `GET /api/v1/assets/{id}/prices` - Get asset prices

### **📈 Portfolio Assets**
- `POST /api/v1/portfolios/{id}/assets` - Add asset to portfolio
- `GET /api/v1/portfolios/{id}/assets` - Get portfolio assets
- `PUT /api/v1/portfolios/{id}/assets/{asset_id}` - Update portfolio asset
- `DELETE /api/v1/portfolios/{id}/assets/{asset_id}` - Remove asset from portfolio

### **💰 Transactions**
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions` - Get user transactions
- `GET /api/v1/transactions/{id}` - Get specific transaction
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction
- `GET /api/v1/transactions/{portfolio_id}/summary` - Transaction summary

### **📊 Analytics**
- `GET /api/v1/analytics/performance/{portfolio_id}` - Portfolio performance
- `GET /api/v1/analytics/risk/{portfolio_id}` - Portfolio risk metrics
- `GET /api/v1/analytics/benchmark/{portfolio_id}` - Benchmark comparison
- `GET /api/v1/analytics/reports/daily/{portfolio_id}` - Daily portfolio report
- `GET /api/v1/analytics/reports/summary` - User portfolios summary

### **📈 Market Data**
- `GET /api/v1/stock/symbols` - Search stock symbols
- `GET /api/v1/stock/symbol-data/fresh` - Get fresh stock data
- `GET /api/v1/stock/symbol-data/local` - Get local stock data
- `GET /api/v1/stock/symbol-data` - Get intelligent stock data

### **📊 Statistical Indicators**
- `GET /api/v1/statistical-indicators/momentum-rsi-indicator` - RSI indicator

## 🎯 **Recommended Testing Flow**

### **1. Authentication Setup**
```bash
1. Register User → Get user_id
2. Login User → Get auth_token
```

### **2. Portfolio Management**
```bash
3. Create Portfolio → Get portfolio_id
4. Get User Portfolios → Verify portfolio created
5. Get Portfolio by ID → Verify portfolio details
6. Update Portfolio → Test modifications
7. Get Portfolio Summary → View metrics
```

### **3. Asset Management**
```bash
8. Create Asset → Get asset_id
9. Get Assets → List all assets
10. Add Asset to Portfolio → Link asset to portfolio
11. Get Portfolio Assets → Verify asset added
12. Update Portfolio Asset → Test modifications
```

### **4. Transaction Management**
```bash
13. Create Transaction → Get transaction_id
14. Get User Transactions → List all transactions
15. Get Transaction Summary → View portfolio activity
```

### **5. Analytics & Reports**
```bash
16. Get Portfolio Performance → View returns
17. Get Portfolio Risk Metrics → View risk analysis
18. Get Daily Portfolio Report → View daily summary
```

### **6. Market Data (Optional Authentication)**
```bash
19. Search Stock Symbols → Find stock symbols
20. Get Fresh Stock Data → Fetch live data
21. Get RSI Indicator → Calculate technical indicators
```

## 🔄 **Automatic Variable Management**

The collection automatically manages these variables through **Postman Tests**:

### **After Registration:**
```javascript
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.collectionVariables.set('user_id', response.id);
}
```

### **After Login:**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.collectionVariables.set('auth_token', response.access_token);
}
```

### **After Portfolio Creation:**
```javascript
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.collectionVariables.set('portfolio_id', response.id);
}
```

### **After Asset Creation:**
```javascript
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.collectionVariables.set('asset_id', response.id);
}
```

### **After Transaction Creation:**
```javascript
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.collectionVariables.set('transaction_id', response.id);
}
```

## 🚨 **Important Notes**

### **Authentication Requirements**
- **Most endpoints require authentication** (Bearer token)
- **Market data endpoints** have optional authentication with rate limiting
- **Statistical indicators** have optional authentication with rate limiting

### **Rate Limiting**
- **Unauthenticated users**: Limited requests per hour
- **Authenticated users**: Higher rate limits
- **Premium features**: Available only to verified users

### **Data Flow**
1. **Create** resources first (user, portfolio, asset)
2. **Link** resources together (add assets to portfolios)
3. **Record** transactions (buy/sell/dividend)
4. **Analyze** performance and risk metrics

### **Error Handling**
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (invalid/missing token)
- **403**: Forbidden (access denied)
- **404**: Not Found (resource doesn't exist)
- **429**: Too Many Requests (rate limited)

## 🧪 **Testing Tips**

### **1. Use Collection Runner**
- Select multiple requests to run in sequence
- Useful for testing complete workflows

### **2. Monitor Console**
- View automatic variable assignments
- Debug authentication issues

### **3. Check Response Headers**
- Verify authentication is working
- Monitor rate limiting headers

### **4. Test Error Scenarios**
- Try invalid tokens
- Test with missing required fields
- Verify access control

## 🔧 **Troubleshooting**

### **Token Not Working**
1. Check if login was successful
2. Verify `auth_token` variable is set
3. Check collection authentication settings

### **Variables Not Updating**
1. Check Postman Tests in each request
2. Verify response status codes
3. Check console for errors

### **Rate Limiting Issues**
1. Authenticate to get higher limits
2. Wait for rate limit window to reset
3. Check rate limit headers in responses

## 📚 **Additional Resources**

- **API Documentation**: Available at `/docs` when running the API
- **Health Check**: `/health` endpoint for API status
- **OpenAPI Schema**: `/openapi.json` for API specification

---

## 🎉 **Ready to Test!**

Your Postman collection is now fully configured with:
- ✅ **Automatic authentication** for all protected endpoints
- ✅ **Smart variable management** for IDs and tokens
- ✅ **Complete API coverage** for all operations
- ✅ **Rate limiting support** for public endpoints
- ✅ **Error handling** and validation

Start with the authentication flow and then explore all the portfolio management features! 🚀
