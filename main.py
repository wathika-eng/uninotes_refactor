import requests
from bs4 import BeautifulSoup
import csv
import re

# Target URL (you can loop over multiple departments if needed)
url = "https://www.jkuat.ac.ke/programmes-bachelor/"

response = requests.get(
    url, verify=False
)  # Use verify=False only if you trust the source
soup = BeautifulSoup(response.content, "html.parser")

# Define keywords to filter
keywords = ("bachelor", "bsc")

# Find all course-related <li> tags (you may need to adjust the selector)
courses = []
for li in soup.find_all("li"):
    text = li.get_text(strip=True)
    if text.lower().startswith(keywords):
        courses.append(text)

# Remove duplicates
courses = list(set(courses))

# Save to CSV
with open("filtered_courses.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Course Name"])
    for course in courses:
        writer.writerow([course])

print(f"{len(courses)} filtered courses saved to filtered_courses.csv ✅")
