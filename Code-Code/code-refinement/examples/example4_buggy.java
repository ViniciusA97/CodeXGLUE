// Bug: Off-by-one error in loop condition
public void processArray(int[] array) {
    for (int i = 0; i <= array.length; i++) {
        System.out.println(array[i]);
    }
}
