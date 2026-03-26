// Fixed: Correct method call
public String getFirstName(String fullName) {
    return fullName.substring(0, fullName.lastIndexOf(" "));
}
