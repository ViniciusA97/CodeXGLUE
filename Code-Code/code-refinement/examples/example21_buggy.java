// Bug: Infinite loop - wrong increment
public void printNumbers(int n) {
    for (int i = 0; i < n; i--) {
        System.out.println(i);
    }
}
