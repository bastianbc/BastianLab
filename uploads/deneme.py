import random

list1 = [
    {"name": "a", "value": "1"},
    {"name": "b", "value": "2"},
    {"name": "c", "value": "3"},
    {"name": "d", "value": "4"}
]

list2 = [
    {"name": "a", "value": "6"},
    {"name": "b", "value": "7"},
    {"name": "c", "value": "8"},
    {"name": "d", "value": "9"}
]

# Rastgele bir öğe seç
random_item_index = random.randint(0, len(list1) - 1)
selected_item = list1[random_item_index]

# Seçilen öğenin değerini list2'deki ile takas et
selected_item["value"], list2[random_item_index]["value"] = list2[random_item_index]["value"], selected_item["value"]

print("List1 (after swap):", list1)
print("List2 (after swap):", list2)
