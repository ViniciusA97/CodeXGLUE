// Fixed: Appropriate exception type
public void validateAge(int age) throws IllegalArgumentException {
    if (age < 0) throw new IllegalArgumentException("Invalid age");
}
