import rocketreach

API_KEY = "19bbbb1k5978103faaf65b0a7f25b80b8ea9aa6f"

def test_api_key():
    try:
        rr = rocketreach.Gateway(api_key=API_KEY)

        # Do a very basic search (safe test)
        s = rr.person.search().filter(current_employer="SomeFakeCompanyThatDoesNotExistXYZ")
        result = s.execute()

        print("✅ API key is valid! RocketReach responded.")
        print("Response object:", result)

    except Exception as e:
        print("❌ API key is not valid or request failed")
        print("Error:", e)

if __name__ == "__main__":
    test_api_key()
