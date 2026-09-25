/*
 * Symbian-X86 LOOX OS - Client-Server IPC Implementation
 * File: symbian_ipc.cpp
 */

#include "symbian_ipc.h"
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>

void RMessage2::Complete(TInt /*aReason*/) {
    // Message completion handled via return code or socket reply
}

CSession2::CSession2() {
}

CSession2::~CSession2() {
}

CServer2::CServer2(TPriority aPriority) 
    : CActive(aPriority), iListenSocketFd(-1) {
}

CServer2::~CServer2() {
    DoCancel();
    if (iListenSocketFd >= 0) {
        close(iListenSocketFd);
        unlink(iServerName.c_str());
    }
}

void CServer2::StartL(const TDesC8& aName) {
    char path[256];
    std::string sName((const char*)aName.Ptr(), aName.Length());
    snprintf(path, sizeof(path), "/tmp/.symbian_ipc_%s", sName.c_str());
    iServerName = path;

    unlink(path);

    iListenSocketFd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (iListenSocketFd < 0) User::Leave(KErrGeneral);

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);

    if (bind(iListenSocketFd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(iListenSocketFd);
        User::Leave(KErrAlreadyExists);
    }

    if (listen(iListenSocketFd, 8) < 0) {
        close(iListenSocketFd);
        User::Leave(KErrGeneral);
    }

    fcntl(iListenSocketFd, F_SETFL, O_NONBLOCK);
    CActiveScheduler::Add(this);
    SetActive();
}

void CServer2::RunL() {
    struct sockaddr_un clientAddr;
    socklen_t clientLen = sizeof(clientAddr);
    int clientFd = accept(iListenSocketFd, (struct sockaddr*)&clientAddr, &clientLen);

    if (clientFd >= 0) {
        // Read incoming message
        RMessage2 msg;
        ssize_t n = read(clientFd, &msg, sizeof(msg));
        if (n == sizeof(msg)) {
            CSession2* session = NewSessionL(msg);
            if (session) {
                try {
                    session->ServiceL(msg);
                } catch (const XLeaveException& e) {
                    msg.iFunction = e.iReason;
                }
                // Send back result
                write(clientFd, &msg, sizeof(msg));
                delete session;
            }
        }
        close(clientFd);
    }

    SetActive();
}

void CServer2::DoCancel() {
    // Clean up
}

RSessionBase::RSessionBase() : iSocketFd(-1) {
}

RSessionBase::~RSessionBase() {
    Close();
}

TInt RSessionBase::CreateSession(const TDesC8& aServerName) {
    char path[256];
    std::string sName((const char*)aServerName.Ptr(), aServerName.Length());
    snprintf(path, sizeof(path), "/tmp/.symbian_ipc_%s", sName.c_str());

    iSocketFd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (iSocketFd < 0) return KErrGeneral;

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);

    if (connect(iSocketFd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(iSocketFd);
        iSocketFd = -1;
        return KErrNotFound;
    }

    return KErrNone;
}

void RSessionBase::Close() {
    if (iSocketFd >= 0) {
        close(iSocketFd);
        iSocketFd = -1;
    }
}

TInt RSessionBase::SendReceive(TInt aFunction, const TInt aArgs[4]) {
    if (iSocketFd < 0) return KErrBadHandle;

    RMessage2 msg;
    msg.iFunction = aFunction;
    msg.iClientPid = getpid();
    if (aArgs) {
        for (int i = 0; i < 4; ++i) msg.iArgs[i] = aArgs[i];
    }

    if (write(iSocketFd, &msg, sizeof(msg)) != sizeof(msg)) return KErrCommsLineFail;
    if (read(iSocketFd, &msg, sizeof(msg)) != sizeof(msg)) return KErrCommsLineFail;

    return msg.iFunction;
}

TInt RSessionBase::Send(TInt aFunction, const TInt aArgs[4]) {
    return SendReceive(aFunction, aArgs);
}
