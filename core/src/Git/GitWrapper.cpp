#include "Git/GitWrapper.hpp"
#include <iostream>

GitWrapper::GitWrapper(const std::string& repoPath) : repoPath(repoPath), repo(nullptr) {
    git_libgit2_init();
    if (git_repository_open(&repo, repoPath.c_str()) != 0) {
        std::cerr << "Failed to open repository at " << repoPath << std::endl;
        repo = nullptr;
    }
}

GitWrapper::~GitWrapper() {
    if (repo) git_repository_free(repo);
    git_libgit2_shutdown();
}

bool GitWrapper::gitPull(const std::string& remote, const std::string& branch) {
    // libgit2 requires fetch + merge manually
    git_remote* rem = nullptr;
    if (git_remote_lookup(&rem, repo, remote.c_str()) != 0) {
        std::cerr << "Remote not found: " << remote << std::endl;
        return false;
    }
    if (git_remote_fetch(rem, nullptr, nullptr, nullptr) != 0) {
        std::cerr << "Fetch failed" << std::endl;
        git_remote_free(rem);
        return false;
    }
    git_remote_free(rem);
    // Merge step is more complex; simplified here
    std::cout << "Pull completed (fetch only). Merge logic needs to be added." << std::endl;
    return true;
}

bool GitWrapper::gitPush(const std::string& remote, const std::string& branch) {
    git_remote* rem = nullptr;
    if (git_remote_lookup(&rem, repo, remote.c_str()) != 0) {
        std::cerr << "Remote not found: " << remote << std::endl;
        return false;
    }
    if (git_remote_push(rem, nullptr, nullptr) != 0) {
        std::cerr << "Push failed" << std::endl;
        git_remote_free(rem);
        return false;
    }
    git_remote_free(rem);
    return true;
}

bool GitWrapper::gitMerge(const std::string& branch) {
    // Simplified: just checkout branch
    return checkoutBranch(branch);
}

bool GitWrapper::gitCreateBranch(const std::string& branch) {
    git_reference* head = nullptr;
    if (git_repository_head(&head, repo) != 0) return false;

    git_commit* commit = nullptr;
    git_commit_lookup(&commit, repo, git_reference_target(head));

    git_reference* newBranch = nullptr;
    int err = git_branch_create(&newBranch, repo, branch.c_str(), commit, 0);
    git_commit_free(commit);
    git_reference_free(head);
    if (err != 0) {
        std::cerr << "Branch creation failed" << std::endl;
        return false;
    }
    git_reference_free(newBranch);
    return true;
}

bool GitWrapper::gitRenameBranch(const std::string& oldName, const std::string& newName) {
    git_reference* branchRef = nullptr;
    if (git_branch_lookup(&branchRef, repo, oldName.c_str(), GIT_BRANCH_LOCAL) != 0) return false;
    int err = git_branch_move(&branchRef, branchRef, newName.c_str(), 0);
    git_reference_free(branchRef);
    return err == 0;
}

bool GitWrapper::gitRebase(const std::string& branch) {
    std::cout << "Rebase requires advanced libgit2 usage (git_rebase_* APIs)." << std::endl;
    return false;
}

bool GitWrapper::gitStash(const std::string& message) {
    int err = git_stash_save(nullptr, repo, nullptr, message.c_str(), GIT_STASH_DEFAULT);
    return err == 0;
}

bool GitWrapper::gitReset(const std::string& commit, const std::string& mode) {
    git_object* target = nullptr;
    if (git_revparse_single(&target, repo, commit.c_str()) != 0) return false;

    git_reset_t resetType = GIT_RESET_HARD;
    if (mode == "soft") resetType = GIT_RESET_SOFT;
    else if (mode == "mixed") resetType = GIT_RESET_MIXED;

    int err = git_reset(repo, target, resetType, nullptr);
    git_object_free(target);
    return err == 0;
}

std::vector<std::string> GitWrapper::getModifiedFiles() {
    std::vector<std::string> files;
    git_status_options opts = GIT_STATUS_OPTIONS_INIT;
    git_status_list* status;
    if (git_status_list_new(&status, repo, &opts) != 0) return files;

    size_t count = git_status_list_entrycount(status);
    for (size_t i = 0; i < count; ++i) {
        const git_status_entry* s = git_status_byindex(status, i);
        if (s->head_to_index) {
            files.push_back(s->head_to_index->new_file.path);
        }
    }
    git_status_list_free(status);
    return files;
}

bool GitWrapper::checkoutBranch(const std::string& branch) {
    git_object* treeish = nullptr;
    if (git_revparse_single(&treeish, repo, branch.c_str()) != 0) return false;
    int err = git_checkout_tree(repo, treeish, nullptr);
    git_object_free(treeish);
    return err == 0;
}

bool GitWrapper::gitDeleteBranch(const std::string& branch) {
    git_reference* branchRef = nullptr;

    // Lookup the branch reference
    if (git_branch_lookup(&branchRef, repo, branch.c_str(), GIT_BRANCH_LOCAL) != 0) {
        std::cerr << "Branch not found: " << branch << std::endl;
        return false;
    }

    // Delete the branch
    int err = git_branch_delete(branchRef);
    git_reference_free(branchRef);

    if (err != 0) {
        std::cerr << "Failed to delete branch: " << branch << std::endl;
        return false;
    }

    std::cout << "Branch '" << branch << "' deleted successfully.\n";
    return true;
}


bool GitWrapper::cloneRepository(const std::string& remoteUrl,
                                 const std::string& localPath,
                                 std::string& errorMessage) {
    git_libgit2_init();
    git_repository* repo = nullptr;
    int rc = git_clone(&repo, remoteUrl.c_str(), localPath.c_str(), nullptr);
    if (rc != 0) {
        const git_error* e = git_error_last();
        if (e && e->message) {
            errorMessage = std::string("git_clone failed: ") + e->message;
        } else {
            errorMessage = "git_clone failed with code " + std::to_string(rc);
        }
        git_libgit2_shutdown();
        return false;
    }
    git_repository_free(repo);
    git_libgit2_shutdown();
    return true;
}