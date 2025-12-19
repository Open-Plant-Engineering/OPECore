#ifndef GITWRAPPER_HPP
#define GITWRAPPER_HPP

#include <string>
#include <vector>
#include <git2.h>

class GitWrapper {
public:
    explicit GitWrapper(const std::string& repoPath);
    ~GitWrapper();

    // Core Git operations
    bool gitPull(const std::string& remote = "origin", const std::string& branch = "main");
    bool gitPush(const std::string& remote = "origin", const std::string& branch = "main");
    bool gitMerge(const std::string& branch);
    bool gitCreateBranch(const std::string& branch);
    bool gitRenameBranch(const std::string& oldName, const std::string& newName);
    bool gitRebase(const std::string& branch);
    bool gitStash(const std::string& message = "WIP");
    bool gitReset(const std::string& commit = "HEAD~1", const std::string& mode = "hard");
    bool gitDeleteBranch(const std::string& branch);

    // Utility
    std::vector<std::string> getModifiedFiles();

private:
    git_repository* repo;
    std::string repoPath;

    bool checkoutBranch(const std::string& branch);
};

#endif // GITWRAPPER_HPP