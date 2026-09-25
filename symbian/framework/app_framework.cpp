/*
 * Symbian-X86 LOOX OS - Avkon Application Framework Implementation
 * File: app_framework.cpp
 */

#include "app_framework.h"

CAknView::CAknView() {
}

CAknView::~CAknView() {
}

CAknAppUi::CAknAppUi() : iCurrentView(NULL) {
}

CAknAppUi::~CAknAppUi() {
    for (size_t i = 0; i < iViews.size(); ++i) {
        delete iViews[i];
    }
}

void CAknAppUi::ConstructL() {
}

void CAknAppUi::HandleCommandL(TInt aCommand) {
    if (aCommand == EAknCmdExit) {
        CActiveScheduler::Stop();
    }
}

void CAknAppUi::HandleResourceChange(TInt aType) {
    if (aType == KEikMessageLowMemory) {
        // Drop transient caches to conserve RAM on Intel Atom
    }
}

void CAknAppUi::AddViewL(CAknView* aView) {
    User::LeaveIfNull(aView);
    aView->ConstructL();
    iViews.push_back(aView);
}

void CAknAppUi::SetDefaultViewL(const CAknView& aView) {
    ActivateViewL(aView.Id());
}

void CAknAppUi::ActivateViewL(TUid aViewId) {
    for (size_t i = 0; i < iViews.size(); ++i) {
        if (iViews[i]->Id() == aViewId) {
            if (iCurrentView) {
                iCurrentView->DoDeactivate();
            }
            iCurrentView = iViews[i];
            iCurrentView->DoActivateL();
            return;
        }
    }
    User::Leave(KErrNotFound);
}

CAknDocument::CAknDocument() : iAppUi(NULL) {
}

CAknDocument::~CAknDocument() {
    delete iAppUi;
}

CAknApplication::CAknApplication() {
}

CAknApplication::~CAknApplication() {
}
