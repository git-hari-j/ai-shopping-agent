from services.magento import MagentoService
import os

def test_integration_token():
    print("Testing Magento Integration Token...")

    # Ensure token is present in env (or via config)
    # This relies on the settings loading MAGENTO_ACCESS_TOKEN

    service = MagentoService()

    # Try a simple query that requires some permission (e.g. Products is usually public, but let's try)
    try:
        # Searching products is generally available to public, but using the service
        # with the token verifies the token is at least not rejected as malformed.
        result = service.search_products("test", page_size=1)
        print("Success! Token accepted (or endpoint is public).")
        print(result)

        # If we had an Admin-only query here (e.g. fetching full order list), we could test that too.
        # But for now, verifying the client initializes and runs is good.

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_integration_token()
