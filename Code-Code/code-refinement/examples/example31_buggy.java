// Bug: Wrong StringBuilder method
public String reverse(String str) {
    return new StringBuilder(str).toString();
}
