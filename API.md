# API Documentation

The backend exposes a WebSocket or REST API (via FastAPI) for the chat interface.

## Magento Integration
The system communicates with Adobe Commerce via GraphQL.

### Configuration
- `MAGENTO_URL`: The base URL of the Magento instance.
- `MAGENTO_ACCESS_TOKEN`: Optional integration token for admin-level access (if needed).

### Key Operations
- `searchProducts`: Catalog search.
- `createEmptyCart` / `addProductsToCart`: Cart management.
- `generateCustomerToken`: User authentication.
- `placeOrder`: Order finalization.

See `ai-agent-backend/services/magento.py` for the implementation details.
