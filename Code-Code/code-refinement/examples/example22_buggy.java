// Bug: Wrong bitwise operator
public boolean hasFlag(int value, int flag) {
    return (value | flag) != 0;
}
