// Bug: String comparison using == instead of equals
public boolean checkPassword(String input, String stored) {
    return input == stored;
}
