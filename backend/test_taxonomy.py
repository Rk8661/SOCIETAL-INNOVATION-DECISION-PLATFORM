from app.services.ai.pipeline import classifier, DOMAIN_LABELS, SUBDOMAIN_MAP, calculate_priority

test_cases = [
    "Village has contaminated drinking water",
    "Primary school roof collapsed",
    "PHC has no essential medicines",
    "Farmers cannot access irrigation water",
    "Streetlights are not working",
    "Waste is accumulating near houses",
    "Village road has severe potholes",
    "School has shortage of teachers",
    "Electricity supply fails every day",
    "Pregnant women have no nearby emergency transport",
    "The village school has no drinking water" # The problematic phrase
]

print(f"\n{'CITIZEN REPORT':<50} | {'DOMAIN':<22} | {'SUBDOMAIN':<25} | {'PRIORITY'}")
print("-" * 115)

for text in test_cases:
    # 1. Domain
    domain_result = classifier(text, DOMAIN_LABELS)
    domain = domain_result["labels"][0]

    # 2. Subdomain
    candidate_subdomains = SUBDOMAIN_MAP.get(domain)
    if candidate_subdomains:
        sub_result = classifier(text, candidate_subdomains)
        subdomain = sub_result["labels"][0]
    else:
        subdomain = "None"

    # 3. Priority
    priority = calculate_priority(subdomain, text)

    print(f"{text[:48]:<50} | {domain[:20]:<22} | {subdomain[:23]:<25} | {priority}")
print("\n")