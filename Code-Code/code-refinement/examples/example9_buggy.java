// Bug: Wrong method call
public String getFirstName(String fullName) {
    return fullName.substring(0, fullName.indexOf(" "));
}
