import rocketreach
API_KEY = "19bbbb1k5978103faaf65b0a7f25b80b8ea9aa6f"
rr = rocketreach.Gateway(api_key=API_KEY)
try:
    result = rr.person.lookup(linkedin_url="https://www.linkedin.com/in/")
    if hasattr(result, "person"):
        print("Name:", result.person.name)
        print("Title:", result.person.current_title)
        print("Company:", result.person.current_employer)
        print("Emails:", result.person.emails)
        print("Phones:", result.person.phones)
    else:
        print("No details found:", result)
except Exception as e:
    print("Error:", e)
try:
    s = rr.person.search().filter(current_employer="thames water stm", current_title="OPERATIONS MANAGER")
    result = s.execute()
    for person in result.people:
        print("Name:", person.name)
        print("LinkedIn:", person.linkedin_url)
        print("Emails:", person.emails)
except Exception as e:
    print("Error:", e)
