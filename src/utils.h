#pragma once

std::string print_hex(const char* data, std::size_t length) {
  std::ostringstream hex_str;
  for (std::string::size_type i = 0; i < length; i++) {
    hex_str << std::hex << std::setw(2) << std::setfill('0')
            << (unsigned short)(unsigned char)data[i] << " ";
  }
  return hex_str.str();
}
