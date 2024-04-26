import struct

class SaveFile:
    SECTION_SIZE = 0x1000
    SIGNATURE = 0x08012025

    def __init__(self, path):
        with open(path, "rb") as f:
            self.data = f.read()

    def get_section(self, offset):
        section_data = self.data[offset:offset+self.SECTION_SIZE]
        data, section_id, checksum, signature, save_index = struct.unpack("<3968sHHL", section_data)
        return {
            "data": data,
            "section_id": section_id,
            "checksum": checksum,
            "signature": signature,
            "save_index": save_index
        }

    def calculate_checksum(self, data, size):
        checksum = 0
        for i in range(0, size, 4):
            value, = struct.unpack("<L", data[i:i+4])
            checksum += value

        return (checksum & 0xFFFF) + (checksum >> 16)

    def validate_section(self, section):
        if section["signature"] != self.SIGNATURE:
            return False

        calculated_checksum = self.calculate_checksum(section["data"], self.SECTION_SIZE-8)  # Minus footer size
        return section["checksum"] == calculated_checksum

    def parse_trainer_info(self, data):
        # Example of how to parse the trainer info
        # Note: Exact fields and their lengths need to be known
        return {
            "trainer_name": data[:7].decode("ascii").strip()
        }

    def parse_pokedex_owned(self, data):
        pokedex_owned_bytes = data[0x0028:0x0028+49]
        # Just return a list of bytes for simplicity, you can then interpret these
        return list(pokedex_owned_bytes)

    def display_data(self):
        for i in range(0, len(self.data), self.SECTION_SIZE):
            section = self.get_section(i)
            if self.validate_section(section):
                if section["section_id"] == 0:
                    print("Trainer Info:")
                    print(self.parse_trainer_info(section["data"]))
                elif section["section_id"] == 1:
                    print("Pokédex Owned:")
                    print(self.parse_pokedex_owned(section["data"]))
                else:
                    # For other section IDs, you can continue adding parsers
                    print(f"Section ID: {section['section_id']}")
                    print(section["data"].hex())
                print("-" * 40)

if __name__ == "__main__":
    path = "path_to_your_save_file.sav"
    save = SaveFile(path)
    save.display_data()
