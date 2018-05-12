#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/mm.h>
#include <linux/errno.h>
#include <linux/types.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/delay.h>
#include <linux/syscalls.h>
#include <linux/uaccess.h>
#include <mach/gpio.h>
#include <mach/iomux.h>
#include <linux/utsname.h>

#include <linux/proc_fs.h>
//sys
/*
 * This module shows how to create a simple subdirectory in sysfs called
 * /sys/kernel/kobject-example  In that directory, 3 files are created:
 * "foo", "baz", and "bar".  If an integer is written to these files, it can be
 * later read out of it.
 */
/*
 * The "foo" file where a static variable is read from and written to.
 */
static int val=1;
static ssize_t pls_show(struct kobject *kobj, struct kobj_attribute *attr,
			char *buf)
{
        sprintf(buf,"%d",val);
	return 1;
}

static ssize_t pls_store(struct kobject *kobj, struct kobj_attribute *attr,
			 const char *buf, size_t count)
{
      if (*buf=='1'){
         val=1;
         gpio_direction_output(RK30_PIN1_PB5,GPIO_HIGH);//enable
      }else if(*buf=='0'){
         val=0;
         gpio_direction_output(RK30_PIN1_PB5,GPIO_LOW);//disable
      }
      return 1;
}

static struct kobj_attribute uni_rst_attribute =
	__ATTR(uni_rst, 0666, pls_show, pls_store);



/*
 * Create a group of attributes so that we can create and destroy them all
 * at once.
 */
static struct attribute *attrs[] = {
	&uni_rst_attribute.attr,
	NULL,	/* need to NULL terminate the list of attributes */
};



//platfrom driver 
static int __devinit gs_probe(struct platform_device *pdev) {

   sysfs_create_file(&(pdev->dev.kobj), &uni_rst_attribute.attr);
   return 0;
}

static int __devexit gs_remove(struct platform_device *pdev) {
   return 0;
}
void gs_shutdown(struct platform_device *plt){
}

static struct platform_device gs_platform_device = {
   .name	= "unisound",
   .id          = -1,
};

static int gs_suspend(struct platform_device *dev, pm_message_t state){
   return 0;
}
static int gs_resume(struct platform_device *dev){
   return 0;
}

static struct platform_driver gs_platform_driver = {
   .probe		= gs_probe,
   .remove		= __devexit_p(gs_remove),
   .driver		= {
      .name	= "unisound",
      .owner	= THIS_MODULE,
   },
   .suspend =gs_suspend,
   .resume = gs_resume,
   .shutdown= gs_shutdown,
};

int __init gs_init(void) {
   int ret;
   ret = 0;
   ret = platform_driver_register(&gs_platform_driver);
   if (ret) {
      printk("fail to register gs driver\n");
   } else {
      ret = platform_device_register(&gs_platform_device);

      if (ret) {
         printk("fail to register gs device\n");
         platform_driver_unregister(&gs_platform_driver);
      }
   }

   return ret;
}

void __exit gs_exit(void) {
   platform_device_unregister(&gs_platform_device);
   platform_driver_unregister(&gs_platform_driver);
}

module_init(gs_init);
module_exit(gs_exit);

MODULE_AUTHOR("gs");
MODULE_LICENSE("GPL");
