import struct

class bl_script:
    BL_CMD_ID_IMAGE_DEF      =   1 
    BL_CMD_ID_COPY           =   2 
    BL_CMD_ID_BL_COPY        =   3 
    BL_CMD_ID_EXEC           =   4 
    BL_CMD_ID_COMMIT_EXEC    =   5
    BL_CMD_ID_COMMIT         =   6 
    BL_CMD_ID_EXC_SCRIPT_SET =   7 
    BL_CMD_ID_COMPARE        =   8 
    BL_CMD_ID_HASH_VERIFY    =   9 
    BL_CMD_ID_IMAGE_RESET    =  10 
    BL_CMD_ID_AREA_PROTECT   =  11 
    BL_CMD_ID_APP_HANDSHAKE  =  12
    BL_CMD_ID_SD_INIT        =  13

    BL_SCRIPTS_START = 0x612FB347
    BL_SCRIPTS_STOP = 0x643FB217
    def __init__(self, script_id):
        self.buffer = []
        self.length = 0
        self.script_start(script_id)

    def script_start(self,script_id):
        self.buffer.extend(struct.unpack("4B", struct.pack("I", 0x600FB007)))
        self.buffer.append(0)
        self.buffer.append(0)
        self.buffer.append(0)
        self.buffer.append(script_id)
        self.length += 2

    def cmd_image_def(self, id, type, segments):
        #header
        self.buffer.append(bl_script.BL_CMD_ID_IMAGE_DEF)
        cmd_len = 1+(2+len(segments))
        self.buffer.append(cmd_len)
        #body
        self.buffer.append(id)
        self.buffer.append(type)
        for item in segments:
            self.buffer.extend(struct.unpack("4B", struct.pack("I", item)))
        self.buffer.extend(struct.unpack("4B", struct.pack("I", 0)))
        self.buffer.extend(struct.unpack("4B", struct.pack("I", 0)))
        self.length += cmd_len 

    def cmd_copy(self,id_dest, id_src, blk_sz):
        self.buffer.append(bl_script.BL_CMD_ID_COPY)
        cmd_len = 2
        self.buffer.append(cmd_len)
        #body
        self.buffer.append(id_dest)
        self.buffer.append(id_src)
        self.buffer.extend(struct.unpack("4B", struct.pack("I", blk_sz)))
        self.length += cmd_len 

    def cmd_bl_copy(self,addr, len):
        self.buffer.append(bl_script.BL_CMD_ID_BL_COPY)
        cmd_len = 3
        self.buffer.append(cmd_len)
        self.buffer.extend(struct.unpack("2B", struct.pack("H", 0)))
        self.buffer.extend(struct.unpack("4B", struct.pack("I", addr)))
        self.buffer.extend(struct.unpack("4B", struct.pack("I", len)))
        self.length += cmd_len

    def cmd_exec(self,addr):
        self.buffer.append(bl_script.BL_CMD_ID_EXEC)
        cmd_len = 2
        self.buffer.append(cmd_len)
        self.buffer.extend(struct.unpack("2B", struct.pack("H", 0)))
        self.buffer.extend(struct.unpack("4B", struct.pack("I", addr)))
        self.length += cmd_len

    def cmd_commit_exec(self,addr):
        self.buffer.append(bl_script.BL_CMD_ID_COMMIT_EXEC)
        cmd_len = 2
        self.buffer.append(cmd_len)
        self.buffer.extend(struct.unpack("2B", struct.pack("H", 0)))
        self.buffer.extend(struct.unpack("4B", struct.pack("I", addr)))
        self.length += cmd_len

    def cmd_exc_script_set(self,script_id):
        self.buffer.append(bl_script.BL_CMD_ID_EXC_SCRIPT_SET)
        cmd_len = 1
        self.buffer.append(cmd_len)
        self.buffer.append(script_id)
        self.buffer.append(0)
        self.length += cmd_len

    def cmd_compare(self,id_image1, id_image2):
        self.buffer.append(bl_script.BL_CMD_ID_COMPARE)
        cmd_len = 1
        self.buffer.append(cmd_len)
        self.buffer.append(id_image1)
        self.buffer.append(id_image2)
        self.length += cmd_len

    def cmd_commit(self):
        self.buffer.append(bl_script.BL_CMD_ID_COMMIT)
        cmd_len = 1
        self.buffer.append(cmd_len)
        self.buffer.extend(struct.unpack("2B", struct.pack("H", 0)))
        self.length += cmd_len

    def cmd_image_reset(self,image_id):
        self.buffer.append(bl_script.BL_CMD_ID_IMAGE_RESET)
        cmd_len = 1
        self.buffer.append(cmd_len)
        self.buffer.append(image_id)
        self.buffer.append(0)
        self.length += cmd_len

    def cmd_app_handshake(self):
        self.buffer.append(bl_script.BL_CMD_ID_APP_HANDSHAKE)
        cmd_len = 1
        self.buffer.append(cmd_len)
        self.buffer.extend(struct.unpack("2B", struct.pack("H", 0)))
        self.length += cmd_len
    
    def cmd_sd_init(self,addr):
        self.buffer.append(bl_script.BL_CMD_ID_SD_INIT)
        cmd_len = 2
        self.buffer.append(cmd_len)
        self.buffer.extend(struct.unpack("2B", struct.pack("H", 0)))
        self.buffer.extend(struct.unpack("4B", struct.pack("I", addr)))
        self.length += cmd_len

    @staticmethod
    def page_start(buffer):
        tmp = []
        tmp.extend(struct.unpack("4B", struct.pack("I", bl_script.BL_SCRIPTS_START)))
        tmp.extend(buffer)
        return tmp

    @staticmethod
    def page_stop(buffer):
        buffer.extend(struct.unpack("4B", struct.pack("I", bl_script.BL_SCRIPTS_STOP)))
        return buffer

    def crc16(self):
        crc = 0xffff
        for item in self.buffer[7:]:
            crc = ((crc &0xFFFF)>> 8) & 0x000000FF | ((crc&0xffff) << 8)
            crc = (crc & 0xffff) ^ item
            crc = (crc & 0xffff) ^ ( ((crc & 0xffff) & 0xFF) >> 4)
            crc = (crc & 0xffff) ^ ((crc & 0xffff) << 8) << 4
            crc = (crc & 0xffff) ^ ((((crc & 0xffff) & 0xFF) << 4) << 1)
        
        crc = struct.unpack("2B", struct.pack("H", crc & 0xffff))
        self.buffer[5:7] = crc

    def get(self):
        self.buffer[4] = self.length
        self.crc16()
        return self.buffer