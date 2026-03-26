// Bug: Missing return statement in if block
private void processData() {
    dataList.add("new item");
    isProcessed = false;
    (counter)++;
    if ((counter) == (maxSize.size())) {
        cleanup();
    }
    finalizeProcess();
}
