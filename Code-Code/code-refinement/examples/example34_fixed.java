// Fixed: Better email regex
public boolean isEmail(String email) {
    return email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$");
}
