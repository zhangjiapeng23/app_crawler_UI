function bindShowScreenshot () {
    $("a").click(function () {
        const screenSpan = $(this).next();
        const display = screenSpan.css("display");
        const beforeScreenshotTitle = screenSpan.children("span:contains('before click:')");
        const afterScreenshotTitle = screenSpan.children("span:contains('after click:')");
        const beforeScreenshotImg = screenSpan.children(".before-screenshot");
        console.log(beforeScreenshotImg);
        const afterScreenshotImg = screenSpan.children(".after-screenshot");

        const beforeScreenshotImgSrc = beforeScreenshotImg.attr("src");
        if (!beforeScreenshotImgSrc) {
            const beforeScreenshotTitleId = beforeScreenshotTitle.attr("id");
            console.log("id="+beforeScreenshotTitleId);
            const afterScreenshotTitleId = afterScreenshotTitle.attr("id");
            beforeScreenshotImg.attr("src", beforeScreenshotTitleId);
            afterScreenshotImg.attr("src", afterScreenshotTitleId);
        }

        if (display == "inline") {
            $(this).next().css("display", "none")
        } else {
            $(this).next().css("display", "inline")
        }

    })
}