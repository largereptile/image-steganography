import math

from PIL import Image


class ImageEditor:
    def __init__(self, image_path):
        self.image_path = image_path
        tmp = Image.open(image_path)
        # uh oh no handling for images with transparency :eyes:
        if tmp.mode == 'RGBA':
            self.image = self.pure_pil_alpha_to_color_v2(tmp)
        else:
            self.image = tmp
        self.image.convert("RGB")
        self.pixels = self.image.load()
        self.x = self.image.size[0]
        self.y = self.image.size[1]
        self.size = self.image.size[0] * self.image.size[1]

    @staticmethod
    def pure_pil_alpha_to_color_v2(image, color=(255, 255, 255)):
        """
        Source: http://stackoverflow.com/a/9459208/284318
        """
        image.load()  # needed for split()
        background = Image.new('RGB', image.size, color)
        background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
        return background

    @staticmethod
    def convert_msg(message):
        """Turns string into list of binary"""
        binary = ['{0:08b}'.format(ord(x), 'b') for x in message]
        return binary

    def get_1d_pixel_map(self):
        """Returns the pixels as a list of tuples rather than the 2d array because I found it easier to work with"""
        pixel_list = []
        for j in range(self.image.size[1]):
            for i in range(self.image.size[0]):
                pixel_list.append(self.pixels[i, j])
        return pixel_list

    def encode(self, message):
        """Main encoding function, adds message to image"""
        binary_msg = self.convert_msg(message)
        list_map = self.write_msg_to_1d(binary_msg)
        level_counter = -1
        for x, pixel in enumerate(list_map):
            i = x % self.x
            if i == 0:
                level_counter += 1
            self.pixels[i, level_counter] = tuple(list_map[x])

    def write_msg_to_1d(self, binary):
        """Writes the message to the pixels in a 1d array"""
        list_map = self.get_1d_pixel_map()
        for i in range(len(binary)):
            list_index = i * 3
            if list_index + 2 < len(list_map) and list_index % 3 == 0:
                pixs = list_map[list_index:list_index + 3]
                character = str(binary[i])
                list_map[list_index:list_index + 3] = self.adjust(pixs, character, bool(i == len(binary) - 1))
        return list_map

    def adjust(self, pixels, character, last):
        """Adjusts a set of 3 pixels"""
        for i in range(0, 9):
            pix = list(pixels[math.floor(i / 3)])  # 3 pixels so divides by 3 and rounds down to get index needed
            index = i % 3  # index of the rg or b value
            if i == 8:
                if pix[index] % 2 != 0 and not last:
                    pix[index] = self.alter_pixel(pix[index])
                elif pix[index] % 2 == 0 and last:
                    pix[index] = self.alter_pixel(pix[index])
            else:
                d = int(character[i])
                if pix[index] % 2 == 0 and not d == 0:
                    pix[index] = self.alter_pixel(pix[index])
                elif pix[index] % 2 != 0 and not d == 1:
                    pix[index] = self.alter_pixel(pix[index])
            pixels[math.floor(i / 3)] = pix
        return pixels

    @staticmethod
    def alter_pixel(pixel):
        """Makes value odd or even"""
        if pixel < 255:
            return pixel + 1
        else:
            return pixel - 1

    def extract_bin(self):
        """Retrieves the binary version of the encoded message"""
        pixel_map = self.get_1d_pixel_map()
        msg = []
        for i in range(0, len(pixel_map), 3):
            char_string = ""
            pixs = pixel_map[i:i + 3]
            for pix in pixs:
                for val in pix:
                    char_string += str(val % 2)
            msg.append(char_string)
            if pixs[2][2] % 2 != 0:
                return msg

    def extract_message(self):
        """Converts binary message into an ascii string"""
        binary = self.extract_bin()
        msg = ""
        for character in binary:
            character = character[0:8]
            msg += chr(int(character, 2))
        return msg

    def save_changes(self, filename="out.png"):
        """Made this a function as a handler"""
        self.image.save(filename)
