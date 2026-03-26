// Fixed: Added null check
public int getNameLength(User user) {
    if (user == null) return 0;
    return user.getName().length();
}
