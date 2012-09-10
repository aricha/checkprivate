# checkprivate

Check private headers against new class-dumps.

### How do I use this?

    python check.py iPhonePrivate.h SpringBoard/

### What is `iPhonePrivate.h`?

This assumes your extension lists all the private APIs it uses in a single header file. Here's an example from one of my projects:

    @interface SBIconController : NSObject
    + (id)sharedInstance;
    @property (assign) BOOL isEditing;
    @property (retain) SBFolder *openFolder;
    @end

    @interface SBAwayController : SBAlert
    + (id)sharedAwayController;
    - (BOOL)isLocked;
    @end

    @interface SBBulletinWindowController : NSObject
    @property(readonly, assign, nonatomic) UIWindow *window;
    @property(readonly, assign, nonatomic) UIInterfaceOrientation windowOrientation;
    + (id)sharedInstance;
    - (BOOL)allowsDismissBannerGesture;
    - (BOOL)allowsHideNotificationsGesture;
    - (BOOL)allowsShowNotificationsGesture;
    - (BOOL)isBusy;
    @end

    @interface SBLinenView : UIView
    @end

Since I only list the methods I actually use, this tool simply checks to see if those methods still exist.

### What is `SpringBoard/`?

A folder with a collection of header files for the version of the binary you want to compare against. I suggest using [class-dump-z](http://code.google.com/p/networkpx/wiki/class_dump_z) and its `-H` option to create it. For many extensions, you'll want to use SpringBoard; however, some may want UIKit or a different binary altogether.



