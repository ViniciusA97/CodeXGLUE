// Bug: Wrong exception type
public void validateAge(int age) throws IOException {
    if (age < 0) throw new IOException("Invalid age");
}
