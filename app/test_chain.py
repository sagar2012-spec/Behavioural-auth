from chain import store_hash, get_hash, is_connected

print("Connected:", is_connected())

store_hash("test_pattern", "abc123hashvalue")
print("Stored a test hash")

result = get_hash("test_pattern")
print("Read back:", result)

print("Match:", result == "abc123hashvalue")