#pragma once

typedef std::array<char, 3> message_addr;

enum class channel_id : char {
  init = 0x01,
  usermanager = 0x03,
  charactermanager = 0x04,
  chatserver = 0x06,
  entitymanager = 0x07,
  groupserver = 0x09,
  tradeserver = 0x0a,
  zoneserver = 0x0d,
  posseserver = 0x0f,
};

struct message {
  char id;
  char opcode;
  std::vector<char> data;

  message() {}

  message(char id, char opcode, std::vector<char> data)
      : id(id), opcode(opcode), data(data) {}

  std::size_t write(std::ostream &out) {
    out.write((char *)&id, sizeof(id));
    out.write((char *)&opcode, sizeof(opcode));
    out.write(data.data(), data.size());
    return sizeof(id) + sizeof(opcode) + data.size();
  }

  void read(std::istream &in, int size) {
    size -= sizeof(id) + sizeof(opcode);
    data.resize(size);

    in.read((char *)&id, sizeof(id));
    in.read((char *)&opcode, sizeof(opcode));
    in.read((char *)&data[0], size);
  }
};

struct usermanager_message : public message {
  channel_id id = channel_id::usermanager;
  enum opcode : char {
    connect = 0,
    roster = 1,
  };
};

struct charactermanager_message : public message {
  channel_id id = channel_id::charactermanager;
  enum opcode : char {
    connect = 0,
    created = 2,
    send = 3,
    create = 4,
    select = 5,
  };
};

struct groupserver_message : public message {
  channel_id id = channel_id::groupserver;
  enum opcode : char {
    client_connect = 0,
    connect = 48,
  };
};

struct zoneserver_message : public message {
  channel_id id = channel_id::zoneserver;
  enum opcode : char {
    connect = 0,
    ready = 1,
    instancecount = 5,
    loaded = 6,
  };
};

struct entitymanager_message : public message {
  channel_id id = channel_id::entitymanager;
  enum opcode : char {
    entityupdate = 3,
    endmessage = 6,
    entitycreateinit = 8,
    randomseed = 12,
    interval = 13,
    componentcreate = 50,
    connect = 70,
  };
};
