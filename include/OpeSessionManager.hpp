


class OpeSessionManager {
public:
    OpeSessionManager();
    ~OpeSessionManager();
    
    bool StartSession();
    bool CloseSession();
    int GetNewSessionID();
    
    bool CommitSession();
private:

};