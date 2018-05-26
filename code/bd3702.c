#include<linux/init.h>
#include<linux/module.h>
#include<linux/i2c.h>
#include <linux/regulator/consumer.h>

MODULE_LICENSE("GPL");
/*
A1 A2 B1 B2 C1 C2 DP1 DN DP2 EP1 EN1 EN2 EP2 MIN
 
 
OUTS2 OUTS1 OUTR2 OUTR1 OUTF2 OUTF1 
 
i2c时钟最高400k。salve address 80H
数据格式：msb lsb 高位在前
S |Slave Address |A |Select Address |A |Data |A |P

i2c连续传输时地址自动增加，循环

除了输入选择，低音选择需要手动mute。其他操作都可以advanced switch(不需要mute?)

寄存器设置：
Initial setup 1//
Initial setup 2 //subwoofer 重低音选择
Initial setup 3 //loudness
Input Selector //输入选择
input gain
volume gain
fader  front   //衰减器前
fader  rear    //衰减器后
Mixing
Bass setup     //低音
Middle setup   //中
Treble setup   //高
Initial setup 4 
System Reset 
 
输入Select address 05(hex)： 
A,B,C,D,E1,E2,D diff,E full(值0-8) 
 
*/

static struct i2c_board_info bd3702_info = {
   I2C_BOARD_INFO("bd3702", 0x40),
};

//i2c_new_device(struct i2c_adapter *adap, struct i2c_board_info const *info);
static void bd3702_device(void) {
   struct i2c_adapter *adapter = i2c_get_adapter(6);
   if (adapter != NULL) {
      pr_info("add bd3702 device\n");
      i2c_new_device(adapter, &bd3702_info);
   }
}

//driver
static struct i2c_device_id bd3702_idtable[] = {
   { "bd3702", 0 },
};

static const struct of_device_id bd3702_of_match[] = {
   { .compatible = "lsec,bd3702", },
   { }
};
/*
int readgtxxx(struct i2c_client *client)
{
    unsigned char *buf[5]={0x80, 0x4E};
    struct i2c_msg msgs[2];
    int ret=-1;
    int retries = 0;
    msgs[0].flags = 0;
    msgs[0].addr  = client->addr;
    msgs[0].len   = 2;
    msgs[0].buf   = &buf[0];

    msgs[1].flags = I2C_M_RD;
    msgs[1].addr  = client->addr;
    msgs[1].len   = 2;
    msgs[1].buf   = &buf[2];

    while(retries < 5)
    {
    
	ret = i2c_transfer(client->adapter, msgs, 2);
	if(ret == 2)break;
	retries++;
    }
}*/
static int bd3702_probe(struct i2c_client *client, const struct i2c_device_id *id) {
   int ret = 0;
   printk(KERN_ERR "bd3702 probed\n");

   //reset
   i2c_smbus_write_byte_data(client, 0xfe, 0x81);

   i2c_smbus_write_byte_data(client, 0x01, 0xe7);
   i2c_smbus_write_byte_data(client, 0x02, 0x11);
   i2c_smbus_write_byte_data(client, 0x03, 0x19);
   i2c_smbus_write_byte_data(client, 0x05, 0x0b);
   i2c_smbus_write_byte_data(client, 0x06, 0x05);

   //volume gain
   i2c_smbus_write_byte_data(client, 0x20, 0x80);
   i2c_smbus_write_byte_data(client, 0x28, 0x80);
   i2c_smbus_write_byte_data(client, 0x29, 0x80); 
   i2c_smbus_write_byte_data(client, 0x2b, 0x80);
   i2c_smbus_write_byte_data(client, 0x2a, 0x80);
   i2c_smbus_write_byte_data(client, 0x2c, 0x80);
   i2c_smbus_write_byte_data(client, 0x30, 0xff);

   //bass middle treble
   i2c_smbus_write_byte_data(client, 0x41, 0x10);
   i2c_smbus_write_byte_data(client, 0x44, 0x11);
   i2c_smbus_write_byte_data(client, 0x47, 0x00);
   i2c_smbus_write_byte_data(client, 0x51, 0x04);
   i2c_smbus_write_byte_data(client, 0x54, 0x00);
   i2c_smbus_write_byte_data(client, 0x57, 0x0f);
   i2c_smbus_write_byte_data(client, 0x75, 0x60);
   i2c_smbus_write_byte_data(client, 0x90, 0x30);

   printk(KERN_ERR "set bd3702 %d", ret);
   //i2c_smbus_read_byte_data(client, reg);
   return 0;
}
static int bd3702_remove(struct i2c_client *client) {
   return 0;
}
static struct i2c_driver bd3702_driver = {
   .driver = {
      .name	= "bd3702",
      .of_match_table = of_match_ptr(bd3702_of_match),
   },

   .id_table	= bd3702_idtable,
   .probe	= bd3702_probe,
   .remove	= bd3702_remove,
};

static void vddon(void) {
   int ret = 0;
#if 1
   struct regulator *vddcama0;
   vddcama0 = regulator_get(NULL, "vddcama0");
   if (vddcama0) {
      regulator_set_voltage(vddcama0, 3300000, 3300000);
      ret = regulator_enable(vddcama0);
      pr_info("enable vddcama0\n");
   }
#else
   struct regulator *vddsim2;
   vddsim2 = regulator_get(NULL, "vddvldo");
   if(vddsim2){
      regulator_set_voltage(vddsim2, 1800000, 1800000);
      ret = regulator_enable(vddsim2);
      printk(KERN_INFO "enable vddsim2\n");
   }
#endif
}

static int bd3702_init(void) {
   vddon();
   bd3702_device();

   printk(KERN_ERR "add bd3702 driver\n");
   i2c_add_driver(&bd3702_driver);
   return 0;
}
static void bd3702_exit(void) {
   i2c_del_driver(&bd3702_driver);
}
module_init(bd3702_init);
module_exit(bd3702_exit); 
