/*
 * Symbian-X86 LOOX OS - Avkon Application Framework
 * File: app_framework.h
 */

#ifndef __APP_FRAMEWORK_H__
#define __APP_FRAMEWORK_H__

#include "../api/include/e32base.h"

#define EAknCmdExit          0xEE01
#define EAknCmdOptions       0xEE02
#define KEikMessageLowMemory 0xEE10

class CAknView : public CBase {
public:
    CAknView();
    virtual ~CAknView();
    virtual TUid Id() const = 0;
    virtual void ConstructL() {}
    virtual void DoActivateL() {}
    virtual void DoDeactivate() {}
};

class CAknAppUi : public CBase {
protected:
    std::vector<CAknView*> iViews;
    CAknView* iCurrentView;
public:
    CAknAppUi();
    virtual ~CAknAppUi();

    virtual void ConstructL();
    virtual void HandleCommandL(TInt aCommand);
    virtual void HandleResourceChange(TInt aType);

    void AddViewL(CAknView* aView);
    void SetDefaultViewL(const CAknView& aView);
    void ActivateViewL(TUid aViewId);
};

class CAknDocument : public CBase {
protected:
    CAknAppUi* iAppUi;
public:
    CAknDocument();
    virtual ~CAknDocument();
    virtual CAknAppUi* CreateAppUiL() = 0;
    inline CAknAppUi* AppUi() const { return iAppUi; }
};

class CAknApplication : public CBase {
public:
    CAknApplication();
    virtual ~CAknApplication();
    virtual TUid AppDllUid() const = 0;
    virtual CAknDocument* CreateDocumentL() = 0;
};

/* Application Entry Point */
GLDEF_C TInt E32Main();

#endif /* __APP_FRAMEWORK_H__ */
