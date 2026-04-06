import React, { useEffect } from "react";

import * as pdfjsLib from "pdfjs-dist";
import { PdfLoader, PdfHighlighter } from "react-pdf-highlighter";
import type { IHighlight } from "react-pdf-highlighter";

import "react-pdf-highlighter/dist/style.css";
pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.4.168/pdf.worker.min.mjs";

interface Props {
    pdfUrl: string;
    highlights: Array<IHighlight>;
}

const InteractivePdfViewer: React.FC<Props> = ({ pdfUrl, highlights }) => {

    useEffect(() => {
        if (highlights && highlights.length > 0) {
            // Spam event until the Box appears
            const watcher = setInterval(() => {
                const pages = document.querySelectorAll('.page'); // wait for PDF render
                const drawnHighlights = document.querySelectorAll('.Highlight'); // wait for the black highlight to appear

                if (pages.length > 0) {
                    if (drawnHighlights.length === 0) {
                        // The paper has appeared, but the black highlight has not appeared -> Click the bell to force recalculate the coordinates!
                        window.dispatchEvent(new Event('resize'));
                    } else {
                        // The black highlight has appeared! Success, turn off the bell immediately.
                        clearInterval(watcher);
                    }
                }
            }, 250); // Check every 250ms (1/4 second)

            return () => clearInterval(watcher);
        }
    }, [highlights]);
    console.log("highlights", highlights);
    return (
        <div className="relative h-full w-full overflow-hidden bg-gray-100">
            <PdfLoader
                url={pdfUrl}
                beforeLoad={
                    <div className="flex h-full w-full items-center justify-center font-bold text-rd-darkblue">
                        Loading PDF... (Please wait)
                    </div>
                }
            >
                {(pdfDocument) => (
                    <PdfHighlighter
                        onScrollChange={() => { }}
                        scrollRef={() => { }}
                        pdfDocument={pdfDocument}
                        enableAreaSelection={(event) => event.altKey}
                        onSelectionFinished={() => null}
                        highlightTransform={(
                            highlight,
                            index,
                            _setTip,
                            _hideTip,
                            _viewportToScaled,
                            _screenshot,
                            _isScrolledTo
                        ) => {
                            console.log("highlight", highlight);
                            return (
                                <React.Fragment key={index}>
                                    {/* ONLY RENDER SOLID BLACK BOXES FOR REDACTION */}
                                    {highlight.position.rects.map((rect, i) => (
                                        <div
                                            key={`black-box-${index}-${i}`}
                                            className="absolute pointer-events-none"
                                            style={{
                                                left: `${rect.left}px`,
                                                top: `${rect.top}px`,
                                                width: `${rect.width}px`,
                                                height: `${rect.height}px`,
                                                backgroundColor: "black",
                                                opacity: 1,
                                                zIndex: 40
                                            }}
                                        />
                                    ))}
                                </React.Fragment>
                            );
                        }}
                        highlights={highlights}
                    />

                )}
            </PdfLoader>

        </div>
    );
};

export default InteractivePdfViewer;