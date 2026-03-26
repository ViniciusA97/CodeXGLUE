// Fixed: Added return statement to prevent further execution
private void processData() {
    dataList.add("new item");
    isProcessed = false;
    (counter)++;
    if ((counter) == (maxSize.size())) {
        cleanup();
        return;
    }
    finalizeProcess();
}
