#pragma once

#include <boost/interprocess/streams/bufferstream.hpp>
#include <boost/iostreams/copy.hpp>
#include <boost/iostreams/filter/zlib.hpp>
#include <boost/iostreams/filtering_streambuf.hpp>
#include <constants.h>
#include <messages.h>
#include <utils.h>

typedef std::array<char, 3> addr;

struct packet {
  char type;
  addr src;
  addr dest;
  message msg;

  packet() {}

  packet(char type, addr dest, addr src, message msg)
      : type(type), dest(dest), src(src), msg(msg) {}
};

struct zlib1_packet : public packet {
  std::array<char, 5> unknown{{0, 0, 0, 0, 0}};

  zlib1_packet() {}

  zlib1_packet(char type, addr dest, addr src, message msg)
      : packet(type, dest, src, msg) {}

  // untested
  void write(std::ostream &out) {
    std::stringstream unc, compressed;
    msg.write(unc);
    int uncsize = unc.str().size();

    boost::iostreams::filtering_streambuf<boost::iostreams::input> compressor;
    compressor.push(boost::iostreams::zlib_compressor());
    compressor.push(unc);
    boost::iostreams::copy(compressor, compressed);
    int csize = compressed.str().size() + 12;

    out.write((char *)&type, sizeof(type));
    out.write(dest.data(), dest.size());
    out.write((char *)&csize, sizeof(csize));
    out.write(src.data(), src.size());
    out.write(unknown.data(), unknown.size());
    out.write((char *)&uncsize, sizeof(uncsize));
    boost::iostreams::copy(compressed, out);
  }

  // untested
  void read(std::istream &in) {
    int csize, uncsize;

    in.read((char *)&type, sizeof(type));
    in.read((char *)&dest[0], dest.size());
    in.read((char *)&csize, sizeof(csize));
    csize -= 12;
    in.read((char *)&src[0], src.size());
    in.read((char *)&unknown[0], unknown.size());
    in.read((char *)&uncsize, sizeof(uncsize));

    char buf[max_length];
    boost::iostreams::filtering_streambuf<boost::iostreams::input> decompressor;
    decompressor.push(boost::iostreams::zlib_decompressor());
    decompressor.push(in);
    std::istream decompressed(&decompressor);
    decompressed.read(buf, csize);

    boost::interprocess::bufferstream msgdata(buf, uncsize);
    msg.read(msgdata, uncsize);
  }
};

struct zlib2_packet : public packet {
  std::array<char, 3> unknown{{0, 0, 0}};

  zlib2_packet() {}

  zlib2_packet(char type, addr dest, addr src, message msg)
      : packet(type, dest, src, msg) {}

  // untested
  void write(std::ostream &out) {
    std::stringstream unc, compressed;
    msg.write(unc);
    int uncsize = unc.str().size();

    boost::iostreams::filtering_streambuf<boost::iostreams::input> compressor;
    compressor.push(boost::iostreams::zlib_compressor());
    compressor.push(unc);
    boost::iostreams::copy(compressor, compressed);
    int csize = compressed.str().size() + 4;

    out.write((char *)&type, sizeof(type));
    out.write(unknown.data(), unknown.size());
    out.write((char *)&csize, sizeof(csize));
    boost::iostreams::copy(compressed, out);
    out.write((char *)&uncsize, sizeof(uncsize));
  }

  // untested
  void read(std::istream &in) {
    int csize, uncsize;

    in.read((char *)&type, sizeof(type));
    in.read((char *)&unknown[0], unknown.size());
    in.read((char *)&csize, sizeof(csize));
    csize -= 4;

    char buf[max_length];
    boost::iostreams::filtering_streambuf<boost::iostreams::input> decompressor;
    decompressor.push(boost::iostreams::zlib_decompressor());
    decompressor.push(in);
    std::istream decompressed(&decompressor);
    decompressed.read(buf, csize);
    in.read((char *)&uncsize, sizeof(uncsize));

    boost::interprocess::bufferstream msgdata(buf, uncsize);
    msg.read(msgdata, uncsize);
  }
};

struct zlib3_packet : public packet {
  zlib3_packet() {}

  zlib3_packet(char type, addr dest, addr src, message msg)
      : packet(type, dest, src, msg) {}

  void write(std::ostream &out) {
    std::stringstream unc, compressed;
    msg.write(unc);
    int uncsize = unc.str().size();

    boost::iostreams::filtering_streambuf<boost::iostreams::input> compressor;
    compressor.push(boost::iostreams::zlib_compressor());
    compressor.push(unc);
    boost::iostreams::copy(compressor, compressed);
    int csize = compressed.str().size() + 7;

    out.write((char *)&type, sizeof(type));
    out.write(dest.data(), dest.size());
    out.write((char *)&csize, sizeof(csize));
    out.write(src.data(), src.size());
    out.write((char *)&uncsize, sizeof(uncsize));
    boost::iostreams::copy(compressed, out);
  }

  void read(std::istream &in) {
    int csize, uncsize;

    in.read((char *)&type, sizeof(type));
    in.read((char *)&dest[0], dest.size());
    in.read((char *)&csize, sizeof(csize));
    csize -= 7;
    in.read((char *)&src[0], src.size());
    in.read((char *)&uncsize, sizeof(uncsize));

    char buf[max_length];
    boost::iostreams::filtering_streambuf<boost::iostreams::input> decompressor;
    decompressor.push(boost::iostreams::zlib_decompressor());
    decompressor.push(in);
    std::istream decompressed(&decompressor);
    decompressed.read(buf, csize);

    boost::interprocess::bufferstream msgdata(buf, uncsize);
    msg.read(msgdata, uncsize);
  }
};

struct uncompressed_packet : public packet {
  uncompressed_packet() {}

  uncompressed_packet(char type, addr dest, addr src, message msg)
      : packet(type, dest, src, msg) {}

  // untested
  void write(std::ostream &out) {
    std::stringstream msgdata;
    msg.write(msgdata);
    int size = msgdata.str().size();

    out.write((char *)&type, sizeof(type));
    out.write(dest.data(), dest.size());
    out.write((char *)&size, sizeof(size));
    boost::iostreams::copy(msgdata, out);
  }

  // untested
  void read(std::istream &in) {
    int size;

    in.read((char *)&type, sizeof(type));
    in.read((char *)&dest[0], dest.size());
    in.read((char *)&size, sizeof(size));
    msg.read(in, size);
  }
};
