#include "OpeSessionManager.hpp"

OpeSessionManager::OpeSessionManager() {}
OpeSessionManager::~OpeSessionManager() {}
bool OpeSessionManager::StartSession() { return true; }
bool OpeSessionManager::CloseSession() { return true; }
int OpeSessionManager::GetNewSessionID() { return 0; }
bool OpeSessionManager::CommitSession() { return true; }