// Bug: Unnecessary System.out.println in production code
public User getCurrentUser() {
    System.out.println("Getting current user");
    return this.userService.getCurrentUser();
}
