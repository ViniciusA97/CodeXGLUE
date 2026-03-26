// Bug: Missing null check before method call
public int getNameLength(User user) {
    return user.getName().length();
}
