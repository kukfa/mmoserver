#pragma once

void print_hex(const std::string &data) {
  std::ostringstream hex_str;
  for (unsigned char c : data) {
    hex_str << std::hex << std::setw(2) << std::setfill('0')
            << (unsigned short)c << " ";
  }
  std::cout << hex_str.str() << std::endl;
}
