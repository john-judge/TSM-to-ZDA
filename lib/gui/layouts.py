import PySimpleGUI as sg
from lib.camera_settings import CameraSettings


class Layouts:

    def __init__(self, acqui_data):
        self.acqui_data = acqui_data
        self.plot_size = (1500, 800)
        self.house64 = 'data:image/png;base64,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'
        self.timer64 = 'data:image/png;base64,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'
        self.close64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsSAAALEgHS3X78AAAE30lEQVRIiZ2VXYgdRRqGn6+quvucM/85iRoTNevMBJFEWY0GFQTBC1HBlaz/jMpoFFfXBdmFvdiLvRIEFRHFGBXMjUQhF/6Bol6sSNaIruCNir/R/Dlx5iRzck736e6qby/6JDlx9CIWFN10Ue/7vW+9X7XcDn8bryWPL2vERkNQQPj9Q72K7F3s7Hxb9bZ98L0bj91jt1y23kxNTxIEGUQ/aTYR6WW9cud/Prx01zf7/7FP5EHXHG7Y6bVTpBPLMSegCWKEEMKvkihgjEWDP+FbEjxTa1bjv9l/CsIKF3ypHhUDSFGACCKC956iKKjV6/hfkCjgUNK0TW1oCA3h+EJk8UUBYFCsQaSyRajArUWLnEONcTrT68nTLtZaEKmmMTiUlsREGy9HO0dgcL1y6lgtZrAsEYFexhwxq2buYfru+1mcOo+828UYg4rgUH7OSkY3zbDq1lkaV1yFP9TqEyy18jiBCMF7DjYmOOu+hxifnCSKItZuvp/F6fPJ05TEwE+dHhN33MfpGy4iFAVjf7qF8etvBV9y1IilBApGIMt6TExOM372JKqKqhLFMdOz93Jk6jx+bHVoztzLyj9eiHqP2Gq7O3UlGAuq1RwYDlUwhoChMdSAz3ZxaEeD8T/fBggaAnGtxpqZWdKFBSbOPLMCCQGJItJPdrHw4lOYRgNsBM6dSCDGErIuodtGkhoyPEr68U5svcbI1ZsQY0CV2vAw9ZGRKjEiSBTR/fQjDm9/AddcjqoSul182kYHVDhJauRffUH7wD7ilatxzVOwI6PM7XiJLO2x4rob0CgGVTSEKigidD94j/ltW9Dg0b0/4BfmyQ8ewKUdWLZ6wCIB9SXFXJvQ+hLkc6QeEznHf199jY1rpjh1w0ZUFTGm7z18/tSj2Hffor5shKLdhhJCADMcw7IlKRIkAqkJRIa4LPl6d5c/PPJkBd5vpArcArD+ue101l1Md08bFxuIBUlOyOUggUIAVIl94Kv5wKqtz7L+7r/0bRHEmApcFbwnHhljw6tv0b3kEtK5gDWmj/GbfQAWZbdaztjyPOfP3oN6D8GDCO133uDAvx9CyxKsRX1JMjbBBa+8Rnbl5RSpR35RfXUGfVLnYGFBcTfdwLo77yLkPYy14CLa773JngfuoNy7QOh2WPnw09WVkufUm8s598G/s+eT9wmBJZ1m+sVTFNBc4Wi8vJ3v//kAJk7AOhbf3MGezTfjWwuYCcv8s1s58K+/okWOxDGdjz5g7+YZtKRSoL+igCp5FKVntGk48sTTzDWb1C+4mB833wgETD2CELBjEfNbtyAjo4xdcz27N11L6B5GGoZQhN+26KiSoII9LebnJx9BkggzNIQkyfEdItiRQGvbM7S2bQHJMGN1NO8ds2dQhBORYBCjAFEE1kFSw0QxuAiTJCAGce64vz4gviTkOTJcErIMMRbyDIxg7bHTFnc47clcmpdj43VkeBRJEkytgdTqSL2OiRMkSRDroH9t4EtCUaBZhmYpIUurZ9pFfVnuX+w62xfjeq3D3/6vbifXrT1XkzgWdREmipA4RlwMUYRY21cg/X+lJ5gSbIHGOVovCHmOCSX7DrbMx599icIhVI2cA5c5mC1gbGnITm4oqAOr0PoOXs9g51HAGiITyCDByXDp4KuiaoESmP8/YC0Y5GajmEsAAAAASUVORK5CYII='
        self.psg64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAMAAADXqc3KAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAMAUExURQAAABlbkiVhkyZikyFjmShjkyhlly1mli5nlylnmS5olyppnC5qmi5rmzBpmDBpmTFqmDFqmTFqmjNrmzFrnDNsmzJsnDJtnTFunjNvnzRsmTRtmzVunTVunjVvnzZwnjlxny5toDFvozJwoTNzpjVwoDRzpDRzqDd4rThyojp0ozl1pTt2pjt3pz11ozt4qDl4qTp6rTl6rzx4qD55qTx5qj97qz17rT58rD98rT9+rz5+sEB3pEF9rkB+r0F+sEF/sT2AtD6AtT6Btk+Aqk2CrEOBs0GBtEKCtEGCtUSBskWBs0SCtEWDtUaEtkWFt0aGt0KFuUCEukOGu0eFuEWHu0eJvEiGuUiHukiIuUiIukmJu0uKvEyKvFCAp1CCqlODrVKCrl2Kr1OEs1KGsFWGsFaIsVaPvFqKsl6NsmKNsWeTuG6YvHadvlySwV6UxF+YxW+bxW6dxnKewHGex3SdwHSfx3egwXGizHmgwHqkxnyjxHio0f/RMf7QMv/TMf/SMv3SNf7UOv7UO//UPP/UPf/UPv/VP//WPP/XPv/VQ//WQv7XQ//WRP/XRf/WR//YRv/YSP/YSf/YSv/ZS//aS//ZTf/aTP7aTf7aTv7bT//cT//bUP/cUP7cUv/cU/7cVf/eVf/fVv/eV/7dWP/eWP/eWf/fWv/fW//fYvzcaf/hW//gXP/gXv/gX//hYP/hYf/hY//iYP/jY//gZf/iZP7iZf/jZv/iZ//lZv/jaf/kav7ka//maf/ma//kbf/lbv7mbP/mbv/mb//id//mcP/ncv/nc//ld//ndv/meP/ocf/ocv/oc//odP/odf/odv/peP/pff/qfY+11ZSzz5G41qC81aW/1P/jgf/qiv/qjv7qoMnZ5szb587d6eDm2+fo1+7v3e/x3vXw1fHx3gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJblQd8AAAEAdFJOU////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////wBT9wclAAAACXBIWXMAABcQAAAXEAEYYRHbAAAAGHRFWHRTb2Z0d2FyZQBwYWludC5uZXQgNC4xLjFjKpxLAAABzUlEQVQoU2P4jwNAJZIEuLJA9M2u/iNgAaiEELOgIFPc//+r6puaalvAQmAJdg4pPj4h5oT/2+raWtqaGmAS/PxC/IJAGdbEB7saW5pb20AyQAkFNiFhUSEgkGZNfjizua29u70XJJHr8j+eV0RGVkRMTJb56u2mvt7eSR0gCT2gPsbMGzbi8hJyPDl3OidPnDRlwhagRHbG/zTXe5WSqqqqmpzXb/VMmz5jztSVIDtSWFLvl3Jrampq8ZY8WThj1tx586ZCXFV9t1xRR1tbR6Lw0f6ZC+YvWDAb6tz/xUom+rrGymWPD8xaunjZ0oUgMZBEsYqZqampWsnTY/PWLF+xZhFIHCRRpW5raWFhUPT/3IJ1a9euW/H//5oTYAlDezs7Kwvv//+XbN6wcev6//+3/z8FltDwcrC3N8/7v3rHtu07Nv3/vxVo0CWQhJGPm5ubdf7/TXt279699//JnTA70j38fH19wv//33b00OGj+w6fPXz5KMRVTiH+/gHuFf//7zl+5szZs2fO7YPo+H/FOSIyPMqz5v//g+dAMocvQCX+XwsMjYmNdgSy9p0/d/bgRZAYWOL//4LgoDAwY+++02AaJoEJcEj8/w8A4UqG4COjF7gAAAAASUVORK5CYII='
        self.cpu64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsSAAALEgHS3X78AAAFi0lEQVRIiZ1WS2wbRRj+/5l92O6u7WycTW03xLEd6uBUjVO1hfbSByLQEwhxoIhbCwcuvApUiEOFhAQVEiAOvK4gqoojSEhtgUNApaJKG5qkdWpa1JfcZL3teu3sZmeGQ9ZVGhIJ8Z/+2Vn93//45psBWMMqlcoXxWLxEACAaZpju3btOkkIoZRSsnv37hOmaY4BABSLxUOVSuXzteJIq32klMqyLBuqqhoAAKqqGpTSpKIoSUQESZK6OnuKohiKohiUUpkxtvivWCvWBABEOp1+sr+//5V169ZtnJub+6FUKh3Rdf3hVqv1l6Zp5Ww2ezASifQ0Go3fhoaGjsZisYdardaM4zjTiEgAQHQC4j0HkQghAAC4oiiJRCKxBQBIs9m8oOt6iRASa7VaVwEAYrFYP+e85TjOpXg8PiyE4LZtn/F93wYAgogghOD3AYS+UFW1q1AovGoYxp4wGxIEgS2EEIQQCQCAcx7gkslCCB8AwLbt07Va7SPP8xqdWPdmIElSxDTNfZZlncrn828MDg6+VavVPvF9fy4Wi/X19fUdWJHMfSaEYJlMZgwRpVqtdtQwjD31ev2HIAgWpJGRkS8VRTEMw9g9OTm5v7u7+9GpqamXq9XqxwAAmzZt+oBzjpzzYC0QIQRDRJpIJLanUqmdw8PDX1mW9ZPv+5bkOM5FVVVTiURia1i24rruDQCAUqn09sDAwCHGGEdEadnwlgOJZT5BRMIYc5rN5iXP8+ax0y9N04qc84Vt27aduHjx4uuEED46Ovo95xxEOH1ExKWEhQh9DPe4JEl0fn7+14mJiecQUWo2m7MAgNQ0zb3d3d3bhoaGjrTb7Wld1x/p6uoa2bBhw4uyLGsAEFBKKSIi51xQSjFcIiICIQRDAhDXdWue502Vy+X3hRALqqr2SoODg2/KsmzE4/GNlNJ1nPOF9evXPxYEAbiue7lWq72rKIphmub+GzdufBeNRg1d14cZYx4hhBJClFQqNRbOQlBKo8lkcms+n48vLi5a0vj4+OOKoiTT6fQzjuNcJYRIQRCALMswOzv7LSEk0tPT85TjOBeCIKi12+1rtm3/ruv6FgDgAMB7e3vHgiAAQgh1HOfquXPnXr958+Zx3/dtshopltp7nyEiUtd1rxuG8URfX99B13Un2+32rKIo3ZzztRgMdOfOnT/mcrkX+vv79zcajVOapm3XNC3HGINoNNpnWdZJz/P+TiQSOzRNK6bT6WcjkUh/q9WaQUTIZrMHEFEjhECz2fzL9/2ZkZGRz0zT3JfNZp+WqtXq+5FIJJXL5V5kjLVDdgDnnMVisYFyufxVSFHgnO9gjDFElIvF4jth34ExxgCAIiIyxtq2bZ+5cuXK5wsLC3NSvV4/BQDCsqw/hBBBLpeTO+WF/KdhC0TIHAoAIggCjogYMnjpEBAi27Z96ezZsy90aCoVCoXXVFVNZbPZ/TMzMy9xzr1ljSdhYLHicN0DCkFYWKFnGMamUqn06fXr17/xPG9e0nV9Y6jnWqiAPCydrTm5laxY+pcCABdCcEqprmnag4qiWNLExMTBZWI3Ho/Hd2Qymb1CCBpm+V8AQJZluHPnzum5ubnx8+fPH+iI3apync/nX04mk9vDXihCiMX/K9drXTjJZDK5FRHJ3bt3/9R1/cH/e+Esb0FnkKK3t3ff5s2bv+7p6Rm7devWsXK5/GGhUDjsOM5kNBp9oFKpfKNp2kC9Xv9xdHT0eCaTed513fPhlYmd4CsBOiDQarVmu7q6KpZl/XLt2rVjQggvHo8PTE9PH242m1PpdPrRy5cvf3L79u2fo9GoyRi7U61W3wsDL5fv1V8VjLFF3/ct3/ctAADP86wgCBq+7zcAABljtud5FgCA7/uWLMvWai8KAIB/ACsf4Gh+DNwbAAAAAElFTkSuQmCC'
        self.camera64 = 'data:image/png;base64,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'
        self.checkmark64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsSAAALEgHS3X78AAAD2ElEQVRIibWVe4hUVRzHP+feuTOz82gfrqwu5gM0zTQpS1yfoGQPyc3IjOwlYRElPcDICEP6Q6i/IvojCCIpTA0tSlSqJSvbTLZE0dbWxz4nXWdnxrk7M/feOY/+sHyEa7pt57/z45zP53x/B84R/B/jzeNLgeXADDHE4IeBV2Ihpo6LK1rzNqEhAW9oGw18UhelYeWUGHFL0tx5lqPZyBAI3mi9o8YRm16cWTlsVFLQVwjY2+4SSI2W+j8KXj+ybmwytO69xjo7Wyqzr8sldbaE60ksIdBlhTVo+KuHXppY5azftKzeNsbQkurntOuTKQQobYhFbCgPNsGaA5NDWm94ZlYV7fmAX3pcenIlTucDAqlJRENUxcJQLgwiwfMtYcpq4503JMJjq8M0d+XpyBRJnfUpBpJwyKYqFqbCcSCQg0gQyCeq4qHp90yr5Pd0kY6+ImnXJ1CaeDhEdSJCTSJKzLEHLXhu4oQEuWKZ79uzZAoX2hKPhOn+I6DtuEdfLriC4NE9L4CYhzEP8dH84Hz9kT0NBHLqvMlJmo5nyBQDylITj4RwM5rmw70orcEA0AL8Q/DgN8OBr/DltL8q64G1F52+obomwr6US7boE0hNhRPiVIdHx7H+EvA2sJ0tC3/+e8uFS27c/SS+7ElGrGkbnp5EfV0UArmGxt0Lzq/x5YzKWocz/T4FXyGEINvj0XE410QgJ7Fl4dqL4ecS3PVlJYgdllKzx04ZxqolY8h4mkm315JPl+z+nP8Bd++4hZ2LM/hyuokLCr7Eti28TJnOA5ndGLOUnYtLl+u2YMHnJ4BxY2bWsWj2SA72eoBBG4PnBvy2qwvpq81gVjhJp1Q7q9axLIFVMqSaz3ytfLWEpsbLwgFs6pc1o/R9+e7+eK9joSMWvjR4gSLA4FSGKLS7UyirUmRkbJFTG0VI6N17+oR0/bl8d/+A8HMJAG7bPB7BTmGL8TVz64mMiKGNQSuN0hqvq59CS59Kzq2zo8MrcH/s1V6qMIf9y5uvBL8gALj54xpgG5aYH589klB9BdoYjDY0XJ9k9HURPj2aRZ/ycL/tfouDK17+N/ilAoAbP6wAsRGLB8INI7BGJUAYLGEhLAtLCApfnDymc95NtD4eDMC8ZNiXzNKfSdLbt5K8N6o68nNMwoHqKCAwlkVwKI06ln2MtpWtVwMHBnjspHyNQO1Xe7pRbTmUEchCGbk/laKsdl0tfGBB51OKQM0hUD/ppk7kkTTy11NQku/TuUpdi+DKn/7wdyuAHzDcii0Uykwg/ezJoRMAVL9TCWwFjpJdvfpa4AB/Akx4zQw8GDagAAAAAElFTkSuQmCC'
        self.cookbook64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAYCAIAAAB1KUohAAAACXBIWXMAAAsSAAALEgHS3X78AAADMUlEQVQ4jY1UQUgCWxS9782M5hQzle3NTRGEQdBipCKKECoEg4JaJAqCmyBsYauEaNOqjQtXLSKINuFiKMiwIMtF1iLK2kWRZLUoDRxo5s37ixfSt4+/u7xzz51z7r3nwc7Ojt1uBwCEEPwtWKXL5eIvLy+HhoYIIYIgCIJAKa0Do5RyHPfy8nJycnJ1dcUjhJxOZygUOj09zefzFoulDp5SihCKRqPLy8vJZBI4jgOAo6Mjj8cDABjj/6WdTqdDoRAAfJeyFn8MQohhGADAY4xFUSyVSpIkAYBpmgih+soRQmxm2GazbW5u7u7ujoyMKIrCmP+ePMdxv9nhSqXi8/lmZmb29vay2Syrs1gs8EM/QogQQgipBWOMOzs7397eWlpabDYbAMiyHAwGu7u7mQTWzu/3R6PRxsZG+HERvNVqjcVix8fHfX19Nzc3T09PHo+HUjo1NVUulx8fHwFgbW0tEolQSguFwtbWVpU/rlQqs7Ozc3NzqqrmcjmXy9Xe3m61WgcGBubn5wGgo6NjYWEBAEql0t3dHQBUx8ljjNva2orFYnNzM8/zBwcHFoslGo329/cXCgUA6OnpwRh/fHwsLS3lcjm2qm9wQ0NDPB7f398fHBx8eHjIZrOqqhaLRUmSwuFwPB53OBw+ny+dTn9+ftYujed5AEilUhMTE9U9saTX66WUJhKJmv0dHh4Gg0FgF4YxJoQwANNjGIaiKLFYbHp62ul0Li4umqb5H5crSVIymQwEAolEwu12s6SiKNfX15OTkwDgcDguLi4ikUgVUv0zCIJgs9lUVWWlrP3q6qrf72dfAaCrq2tjY0OW5RowTynVNM1qteq6XqW9srJiGAZCSNd1hNDt7W04HGZm+NeFiaKYTCa3t7fHx8fdbjez+9fXV7UR87Cu66Zp1oI1TQsEAl6vN51Os9smhCCEfpbWmMw0TZbBpmm+v7+3traWy2VKKdP825I/M7Isi6IIAFxTU9P6+nomk+nt7X19fX1+fsYY1/ez0+k8Pz+/v7/nMMblcnl4eDifz5+dnWmaVgfGolQq2e32sbGx7wcok8mMjo7C396wVCpFKSWE/ANWXYLwO0+V8wAAAABJRU5ErkJggg=='
        self.download64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsSAAALEgHS3X78AAAEl0lEQVRIia2WS2hdZRDHf/Odc+7NvbZpYky1Gk2rEbRa26pt8UWLitYHIqigCD426kIQxCfWhYu68U0RBBERXCq+WrXoorYIFWpbEY0lpk0NTWKtuUlzn+d834yLm5smqQspzurMcM785j+c+eYTTtUcESAzvhIAm/+azHacA4FodszAVNFTrUPm+Q6iecmUyJkEna5OiDCCXCtvJ2cnV+Ep+9R7/VIfQhmeryKeySywok+SSMMKMwqAihDXPIcPDDMURUQCgiPWjJCck6x87ZXXV3cXu3XTO5tkYOvAHbnIfZipTpghLdAMIEngi1cXvtlzwfrHpG0x5ismzsvo0E9D9z7z++M799s2EcSm67OUkAs5cpbzkkoMtPtAAzdXQ9zqjHkt1Ol5SHofx0KWYRUxrdiS3FlLtzz51wd7+v2OQl7qHnPtorUXS3ZxPRUKUT5x4mTDWu559LbCNS+9X9v025Duc4KoYdMAA7A4Mk92EMp/JFIZwR/rx9dL1teVdC2/Qe8yzQg+pS0JvLUzx3hjioPVQamGGlcu47KNq6qrPj+fsd+GeAEYA2SmRQiCNSJKP1Ad3IVaG0nnlWRxKqkkVlYxJxGZwhmFIo34U/fh0Hv4v6YYrY+ihYtkorDUNj+298GPvzv6ZRrkMzA/oyCXh9rEMOOHfiLfcx+5zhXkOnppswxEpJHVxdTjs0CycDHy9XcMlwc5a0E3EoTconOls/dyBsb6lYRLY4m/9T6blDgi8oHw3rPx83fesubl4oVPWFvXBUKoQzqB92Xitpite77n/k/epaN7AZO1CTIROtZ14fJC6ccS9ndGUhRLK0Eum1h2YGpH5eFfD47sjluzcFo+f+vp655F03alNhZhASMjloA1qtzedzab125kiw2QLhHaQ0zIFM2MztUdkBcqx1Lp+0o59NGRP49OVQs0Z3d6nEyMUMP8OGgVtAJaA19CagP4xn4e6DPuPhox1V9HTRFr/h9mRmWkwbJtGSsHK4xXq4cQGQDCDABM0ClEy6DlJiA9DLV90BgktirFzhrPXX0mT6Y9lAaqkAhRItRKGT3bjetTYd2aYM7JYcwm5wwaAP44hDyQYukokg5jliICZoFIoNjZ4Ol1HdhueOPgCLlFjt7twvo63HwztGuipml20lEBBlrGfBXzR5BsDGjOPBrAAkJKRKBwuuepNUXyP5/HN7tKXFGvcuMGY/3qhAO/NLCTJ7kFmIT0OPgjmAhiYKYIASFgGoCUyAILu+o8ckng0jSwsF1YuzxP0hYwm3tizwIIpKPQOIY4BXUYCiiYYWSIKYYHMoRAV1fKTddFxJKQOA/mmW9zFWRjoCmYw6R1lrcg2kxgAfCIeRxKMa+YBSw0Vc7fOScAZuAnMXWYE8yaIUFBDFSbS8sCgscsayZWD3jMAmhT7b8CnDPIeZw6RGTOLmwWFRALMA3BZvkamoBcwM3Zh7MA9Yb5I3v/YKoKTlr9sROKZVrlTGDWsylmkMTGxCQ4h0ObGaT1aRJzHsbtwJJmWSet0/9kIpB69gPbgersJA4oMm/pn6JlQI1/uWX87/YP06p9rkZQnAYAAAAASUVORK5CYII='
        self.github64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAMAAADXqc3KAAAABGdBTUEAALGPC/xhBQAAAwBQTFRFAAAADAwMDQ0NAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAhyjGAAAAQB0Uk5T////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////AFP3ByUAAAAJcEhZcwAADdUAAA3VAT3WWPEAAAAYdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjEuMWMqnEsAAABzSURBVChTbYxRFoAgDMPQ+98Z1zbIeJqPbU3RMRfDECqyGpjMg6ivT6NBbKTw5WySq0jKt/sHrXiJ8PwpAAVIgQGkwABSYAApMIAUGEAalFmK9UJ24dC1i7qdj6IO5F+xnxfLu0jS0c7kqxd3Dk+JY8/5AKFrLuM7mfCAAAAAAElFTkSuQmCC'
        self.run64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAMAAADXqc3KAAAABGdBTUEAALGPC/xhBQAAAwBQTFRFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAszD0iAAAAQB0Uk5T////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////AFP3ByUAAAAJcEhZcwAADdUAAA3VAT3WWPEAAAAYdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjEuMWMqnEsAAABqSURBVChTpY5JDsAwCMTy/09TMGvFpVF9aAZPRHpkcXC7OIodPg0uCjPq+MwCrWRGKkiIvLyTqzw3aqoI73eqUNAoXBXlg4zudxF+NONfPIVvbSZPgww5oW0Vz8T4Lgbt/xbjia+rahR5AEYEg4vdzh2JAAAAAElFTkSuQmCC'
        self.storage64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAMAAADXqc3KAAAABGdBTUEAALGPC/xhBQAAAwBQTFRFAAAABwcHDQ0NDg4ODw8PFxcXGRkZGhoaGxsbHh4eIyMjJSUlJiYmJycnKCgoMTExMjIyNTU1NjY2Nzc3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAouNksgAAAQB0Uk5T////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////AFP3ByUAAAAJcEhZcwAADdQAAA3UAe+RuhUAAAAYdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjEuMWMqnEsAAAC5SURBVChTfZLbDsMgDEPpbb3TDv7/W7PYuAztYUeqhO2QAGowkXIMIeYkaSU4QsNBi4GcyhNINpTglmq4GWSphvy/ldkuLXZ4HmAxy3NmFJaA4guKGCwsjClfV05+fWdhYBtFw+amB292aygW3M7fsPTwjmadZkCvHEtWaAYTViBqVwgTA3tJVnB6D/xhaimItDhjMBvlhtFsaIafnEtOaAY/twAw/eslK70CbX8obUvgJNw9Jv0+Zh8D4s5+VAm/LwAAAABJRU5ErkJggg=='

    def create_menu(self):
        menu_def = [['File', ['Choose Data Directory', 'Exit']],
                    ['Preference', ['Save Preference', 'Load Preference'], ]]
        toolbar_buttons = [[sg.Button('', image_data=self.close64[22:],
                                      button_color=('white', sg.COLOR_SYSTEM_DEFAULT),
                                      pad=(0, 0), key='-close-',
                                      tooltip="Exit"),
                            sg.Button('', image_data=self.timer64[22:],
                                      button_color=('white', sg.COLOR_SYSTEM_DEFAULT),
                                      pad=(0, 0), key='-timer-',
                                      tooltip="Schedule a session at the Little Dave rig (Google Calendar)"),
                            sg.Button('', image_data=self.house64[22:],
                                      button_color=('white', sg.COLOR_SYSTEM_DEFAULT),
                                      pad=(0, 0), key='-house-'),
                            sg.Button('', image_data=self.cpu64[22:],
                                      button_color=('white', sg.COLOR_SYSTEM_DEFAULT),
                                      pad=(0, 0), key='-cpu-'),
                            sg.Button('', image_data=self.download64[22:],
                                      button_color=('white', sg.COLOR_SYSTEM_DEFAULT),
                                      pad=(0, 0), key='-download-'),
                            sg.Button('', image_data=self.github64[22:],
                                      button_color=('white', sg.COLOR_SYSTEM_DEFAULT),
                                      tooltip='Technical Docs',
                                      pad=(0, 0), key='-github-'),
                            sg.Button('', image_data=self.psg64[22:],
                                      button_color=('white', sg.COLOR_SYSTEM_DEFAULT),
                                      pad=(0, 0), key='-psg-',
                                      tooltip="Submit an issue to request a bug fix or new feature."),
                            sg.Button('', image_data=self.run64[22:],
                                      button_color=('white', sg.COLOR_SYSTEM_DEFAULT),
                                      pad=(0, 0), key='-run-'),
                            ]]
        layout = [[sg.Menu(menu_def, )],
                  [sg.Frame('', toolbar_buttons, title_color='white',
                            background_color=sg.COLOR_SYSTEM_DEFAULT, pad=(0, 0))],
                  ]
        return layout

    def create_progress_bar(self):
        return [[sg.Text('Progress: '),
        sg.ProgressBar(1000, 
            orientation='h', 
            size=(60, 20), 
            key='progress_bar'),
        sg.Button('Cancel', key='cancel_button', enable_events=True, 
            tooltip='Attempt to cancel the current operation.'),
        sg.Text("Status: Idle", key='status_text')]]

    @staticmethod
    def create_file_browser():
        return [[
            sg.In(size=(25, 1), enable_events=True, key="-FILE-"),
            sg.FileBrowse(key="file_window.browse",
                          # file_types=(("Raw Data Files", "*.zda"))
                          )],
            [sg.Button("Open", key='file_window.open')]]

    def create_ppr_wizard(self):
        return [[[sg.Image(key = 'ppr_wizard_image', size=(400, 400))],],
                [sg.Button('Generate PPR Catalog', key='ppr_generate_catalog',
                           tooltip='Generate an example PPR file for PPR export. \
                           All ZDA files in the data directory will be listed.'),
                 sg.Button('Start Export', key='start_ppr_export',),
                 sg.Button('Regenerate Summary', key='regenerate_ppr_summary',),]]

    def create_roi_wizard(self, controller):
        return [[[sg.Image(key = 'roi_wizard_image', size=(400, 400))],],
                [sg.Text("Decompose ROIs into smaller ones. \n")],
                [sg.Text("ROIs per file: ", size=(12, 1)),
                 sg.InputText(key='roi_wizard_max_rois', size=(8, 1), enable_events=True,
                              default_text=controller.roi_wizard_max_rois, 
                              tooltip='Maximum number of new ROIs to create per original ROI.')],
                [sg.Text("ROI size (px): ", size=(12, 1),),
                 sg.InputText(key='roi_wizard_pixels_per_roi', size=(8, 1), enable_events=True,
                              default_text=controller.roi_wizard_pixels_per_roi, 
                              tooltip='Random: Number of pixels per new ROI. Bands/Stripes: Pixel-width of each stripe.')],
                [sg.Text("ROI Type:"),
                 sg.Combo(controller.roi_wizard_roi_type_options, key='roi_wizard_roi_type', 
                          default_value=controller.roi_wizard_roi_type_options[controller.roi_wizard_roi_type_idx], 
                          enable_events=True, size=(12, 1), 
                          tooltip='Method for creating new ROIs.')],
                [sg.Text("Stripe Direction Keyword: ", size=(20, 1)),
                sg.InputText(key='roi_wizard_stripe_dir_keyword', size=(10, 1), enable_events=True,
                                default_text=controller.roi_wizard_stripe_dir_keyword,
                                tooltip='Keyword to search for in file names to determine stripe direction.' + \
                                    ' File should also contain name of the corresponding ROI file to process.' + \
                                    'Options for selecting a .dat ROI file with the first ROI containing two pixels,' + \
                                    'both lying along the axis along which striped ROIs are to be created.' +\
                                    ' For ladder ROIs, there should be four points (corners of the ladder), ' +\
                                    ' and one end of the ladder should be placed at an edge of the frame.' 
                                         )],
                [sg.Button('Create ROIs', key='roi_wizard_create_rois',)]
                ]

    @staticmethod
    def create_files_browser(tsv_only=False):
        fb = None
        if tsv_only:
            fb = sg.FilesBrowse(key="file_window.browse",
                                file_types=(("Tab-Separated Value file", "*.tsv"),))
        else:
            fb = sg.FilesBrowse(key="file_window.browse")
        return [
            [sg.In(size=(25, 1), enable_events=True, key="-FILE-"),
             fb],
            [sg.Button("Open", key='file_window.open')]]

    @staticmethod
    def create_folder_browser():
        return [[
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(key="folder_window.browse")],
            [sg.Button("Open", key='folder_window.open')]]

    @staticmethod
    def create_save_as_browser(file_types):
        return [[
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FileSaveAs(key="save_as_window.browse", file_types=file_types)],
            [sg.Button("Save", key='save_as_window.open')]]

    def create_file_tab(self, gui):
        button_size = (10, 1)
        field_size = (6, 1)
        long_button_size = (15, 1)
        checkbox_size = (8, 1)
        return [
            [sg.Text("Slice:", size=(8, 1), justification='right'),
             sg.InputText(key="Slice Number",
                          default_text=str(self.acqui_data.get_slice_no()),
                          enable_events=True,
                          size=field_size,
                          tooltip='An index for tracking which brain slice to which this data belongs.'),
             sg.Button('<', key='Decrement Slice', tooltip='Decrement slice number.'),
             sg.Button('>', key='Increment Slice', tooltip='Increment slice number.')],
            [sg.Text("Location:", size=(8, 1), justification='right',
                     tooltip='An index for tracking which electrode location placement to which this data belongs.'),
             sg.InputText(key="Location Number",
                          default_text=str(self.acqui_data.get_location_no()),
                          enable_events=True,
                          size=field_size),
             sg.Button('<', key='Decrement Location', tooltip='Decrement location number.'),
             sg.Button('>', key='Increment Location', tooltip='Inccrement location number.')],
            [sg.Text("Record:", size=(8, 1), justification='right'),
             sg.InputText(key="Record Number",
                          default_text=str(self.acqui_data.get_record_no()),
                          enable_events=True,
                          size=field_size,
                          tooltip='An index for tracking which recording (trial set) to which this data belongs.'),
             sg.Button('<', key='Decrement Record', tooltip="Decrement record number."),
             sg.Button('>', key='Increment Record', tooltip="Increment record number.")],
            [sg.Checkbox('Convert Files on Recording', default=gui.controller.should_convert_files,
                         enable_events=True, key="Convert Files Switch",
                         tooltip="When checked, files are automatically detected "
                                 "and converted to ZDA following recording.")],
            [sg.Checkbox('Use new rig directory', default=gui.controller.new_rig_settings,
                         enable_events=True, key="New rig settings",
                         tooltip="When checked, use directory C:/Turbo-SM/SMDATA/John/")],
            [sg.Checkbox("Use today's date subdirectory (" + gui.controller.today + ")",
                         default=gui.controller.use_today_subdir,
                         enable_events=True, key="Today subdir",
                         tooltip="When checked, auto-create and use a sub-directory of mm-dd-yy")],
            [sg.Button("Record", key='Record', size=button_size),
             sg.Button("Convert New",
                       key='Detect and Convert',
                       size=button_size,
                       tooltip="Detect and convert files in data directory."),
             ]
        ]

    def create_trials_tab(self, gui):
        cell_size = (10, 1)
        double_cell_size = (20, 1)
        return [[sg.Text("Number of Trials:", size=double_cell_size),
                 sg.InputText(key="num_trials",
                              default_text=str(self.acqui_data.get_num_trials()),
                              enable_events=True,
                              size=cell_size,
                              tooltip='Number of trials in each recording.'),
                 sg.Text("", size=cell_size)],
                [sg.Text("Interval between Trials:", size=double_cell_size),
                 sg.InputText(key="int_trials",
                              default_text=str(self.acqui_data.get_int_trials()),
                              enable_events=True,
                              size=cell_size,
                              tooltip='Number of seconds between trials in each recording.'),
                 sg.Text(" s", size=cell_size)],
                [sg.Text("Record (Sets of Trials) Controls")],
                [sg.Text("Number of Recordings:", size=double_cell_size),
                 sg.InputText(key="num_records",
                              default_text=str(self.acqui_data.get_num_records()),
                              enable_events=True,
                              size=cell_size,
                              tooltip='Number of recordings (sets of trials).'),
                 sg.Text("", size=cell_size)],
                [sg.Text("Interval between Record:", size=double_cell_size),
                 sg.InputText(key="int_records",
                              default_text=str(self.acqui_data.get_int_records()),
                              enable_events=True,
                              size=cell_size,
                              tooltip='Number of seconds between recordings (sets of trials).'),
                 sg.Text(" s", size=cell_size)],

                ]

    def create_recording_settings_tab(self, gui):
        cell_size = (10, 1)
        double_cell_size = (20, 1)
        return [
            [sg.Text("Setting:", size=cell_size),
             sg.Combo(CameraSettings().list_settings(),
                      size=double_cell_size,
                      enable_events=True,
                      default_value=gui.controller.cam_settings['display'],
                      key='camera settings')],
            [sg.Text("Points to Collect:", size=double_cell_size),
             sg.InputText(key="Collect Points",
                          default_text=str(self.acqui_data.get_num_points()),
                          enable_events=True,
                          size=cell_size,
                          tooltip='Number of points to collect. May collect extra in TurboSM before shortening.')],
            [sg.Text("Extra Points:", size=double_cell_size),
             sg.InputText(key="Extra Points",
                          default_text=str(self.acqui_data.get_num_extra_points()),
                          enable_events=True,
                          size=cell_size,
                          tooltip='Number of extra points for TurboSM to collect but not pass to PhotoZ files. ' +
                                  'Aids in reducing artifacts while mitigating disk storage issues.'),
             sg.Checkbox("Shorten",
                         default=gui.controller.shorten_recording,
                         enable_events=True,
                         key="Shorten recording",
                         tooltip="When checked, shortens recording length to num_points.")
             ],
            [sg.Text("Points to Discard:", size=double_cell_size),
             sg.InputText(key="Skip Points",
                          default_text=str(self.acqui_data.get_num_skip_points()),
                          enable_events=True,
                          size=cell_size,
                          tooltip='Number of points to discard at beginning of each trial.')
             ],
            [sg.Text("Points to Flatten:", size=double_cell_size),
             sg.InputText(key="Flatten Points",
                          default_text=str(self.acqui_data.get_num_flatten_points()),
                          enable_events=True,
                          size=cell_size,
                          tooltip='Number of points to flatten to trace average at beginning of each trial.'),
             ],
            [sg.Text("Initial Delay:", size=double_cell_size),
             sg.InputText(key="Initial Delay",
                          default_text=str(self.acqui_data.get_init_delay()),
                          enable_events=True,
                          size=cell_size,
                          tooltip='Number minutes to delay before collecting data.'),
             sg.Text(" min")],
        ]

    def create_specialized_rec_tab(self, gui):
        cell_size = (10, 1)
        double_cell_size = (20, 1)
        checkbox_size = (12, 1)
        return [
            [sg.Button("Toggle Fan",
                       key='Fan',
                       size=cell_size,
                       tooltip="Turns fan on or off"),
             sg.Button("TBS",
                       key='Theta Burst Stim',
                       size=cell_size,
                       tooltip="Deliver 4 x 10 x 100 Hz Theta Burst Stimulation (TBS) protocol. If Prizmatix"
                               " Pulser is running on a separate machine, select the correct setting there first.")
             ],
             [sg.Button("Steady State",
                       key='Steady State',
                       size=cell_size,
                       tooltip="Deliver repetitive stimulation at a fixed frequency."),
             sg.Text("Start Frequency (Hz):"),
             sg.InputText(key="SS Start",
                          default_text=str(self.acqui_data.get_steady_state_freq_start()),
                          enable_events=True,
                          size=cell_size,
                          tooltip='Frequency (Hz) of steady state stimulation, start'),
             sg.Text("to"),
             sg.InputText(key="SS End",
                          default_text=str(self.acqui_data.get_steady_state_freq_end()),
                          enable_events=True,
                          size=cell_size,
                          tooltip='Upper limit of Frequency (Hz) of steady state stimulation, Non-inclusive.'),
             ],
             [sg.Text("\tSSinterval:"),
             sg.InputText(key="SS Interval",
                          default_text=str(self.acqui_data.get_steady_state_freq_interval()),
                          enable_events=True,
                          size=cell_size,
                          tooltip='Interval between SS frequencies to record, in Hz.')],
            [sg.Checkbox('Paired Pulse',
                         default=gui.acqui_data.is_paired_pulse_recording,
                         size=checkbox_size,
                         enable_events=True,
                         key="Paired Pulse",
                         tooltip="Integrates with Pulser software to set up PPRs of various " +
                                 "inter-pulse intervals.")],
            [sg.Text("\tIPI:"),
             sg.InputText(key="PPR Start",
                          default_text=str(self.acqui_data.get_ppr_start()),
                          enable_events=True,
                          size=cell_size,
                          tooltip='First IPI in milliseconds.'),
             sg.Text("to"),
             sg.InputText(key="PPR End",
                          default_text=str(self.acqui_data.get_ppr_end()),
                          enable_events=True,
                          size=cell_size,
                          tooltip='Upper limit of IPI to record, in milliseconds. Non-inclusive.'),
             sg.Text("ms")],
            [sg.Text("\tIPI interval:"),
             sg.InputText(key="PPR Interval",
                          default_text=str(self.acqui_data.get_ppr_interval()),
                          enable_events=True,
                          size=cell_size,
                          tooltip='Interval between IPIs to record, in milliseconds.'),
             sg.Checkbox('Create Settings',
                         default=gui.controller.should_create_pulser_settings,
                         size=checkbox_size,
                         enable_events=True,
                         key="Create Pulser IPI Settings",
                         tooltip="If checked, creates all necessary Pulser settings of various " +
                                 "inter-pulse intervals."),
             sg.Checkbox('Single Pulse Control',
                         default=gui.controller.should_take_ppr_control,
                         size=checkbox_size,
                         enable_events=True,
                         key="PPR Control",
                         tooltip="Before each recording, take a recording of a single pulse at " +
                           "the first pulse time, for subtraction in processing.")],
            [sg.Text("\tPulse Alignment:"),
             sg.Combo(gui.controller.ppr_alignment_settings,
                        size=double_cell_size,
                        enable_events=True,
                        default_value=gui.controller.ppr_alignment_settings[gui.controller.ppr_alignment],
                        key='ppr_alignment_settings',
                        tooltip="Where to place the paired pulses with respect to beginning and end of recording." +
                                 "\nIf left, first pulse is at 50ms and second is at 50ms + IPI." +
                                 "\nIf right, first pulse is at (T_end - IPI - margin)"
                                 " and second is at T_end - 50ms." + 
                                 "\nIf center, first pulse is at (T_end - IPI)/2")],
                ]

    def create_auto_tab(self, gui):
        button_size = (20, 1)
        checkbox_size = (8, 1)
        return [[sg.Button('Launch All', size=button_size,
                           key='Launch All', tooltip='Launch/prepare related applications (default excludes Pulser).'),
                 sg.Checkbox('+ Pulser', default=gui.controller.should_auto_launch_pulser,
                             enable_events=True, key="+ Pulser",
                             tooltip="When checked, launch all INCLUDES launching Pulser.")
                ],
                [sg.Button('Launch PhotoZ', size=button_size,
                           key='Launch PhotoZ', tooltip='Launch and prepare PhotoZ.')],
                [sg.Button('Launch TurboSM', size=button_size,
                           key='Launch TurboSM', tooltip='Launch and prepare TurboSM.')],
                [sg.Button('Launch Pulser', size=button_size,
                           key='Launch Pulser', tooltip='Launch and prepare Prizmatix Pulser.')],
                [sg.Button('Empty Recycle Bin', size=button_size,
                           key='Empty Recycle Bin', tooltip='When you need more disk space.')],
                [sg.Button('View Data Folder', size=button_size,
                           key='View Data Folder',
                           tooltip='File Explorer to manage recording files.')],
                ]

    @staticmethod
    def create_analysis_tab(gui):
        button_size = (15, 1)
        checkbox_size = (12, 1)
        field_size = (8, 1)
        return [
            [sg.Text("Export:", size=(14,1)),
            sg.Checkbox('MaxAmp', size=checkbox_size, key="Amplitude Trace Export",
                            enable_events=True, default=gui.controller.is_export_amp_traces,
                            tooltip="Export traces of amplitude to PhotoZ dat files."),
            sg.Checkbox('SNR', size=checkbox_size, key="SNR Trace Export",
                            enable_events=True, default=gui.controller.is_export_snr_traces,
                            tooltip="Export traces of SNR to PhotoZ dat files."),],
            [sg.Checkbox('Latency', size=checkbox_size, key="Latency Trace Export",
                            enable_events=True, default=gui.controller.is_export_latency_traces,
                            tooltip="Export traces of latency to PhotoZ dat files."),
             sg.Checkbox('Half-width', size=checkbox_size, key="Halfwidth Trace Export",
                            enable_events=True, default=gui.controller.is_export_halfwidth_traces,
                            tooltip="Export traces of half-width to PhotoZ dat files."),
             sg.Checkbox('Traces', size=checkbox_size, key="Trace Export",
                            enable_events=True, default=gui.controller.is_export_traces,
                            tooltip="Export traces to PhotoZ dat files."),
             sg.Checkbox("Non-polyfit traces", size=checkbox_size, key='Trace_export_non_polyfit', 
                            enable_events=True, default=gui.controller.is_export_traces_non_polyfit,
                            tooltip="Export traces without polynomial fit to PhotoZ dat files.")],
            [sg.Checkbox("SD", size=checkbox_size, key="SD Export",
                        enable_events=True, default=gui.controller.is_export_sd_traces,
                        tooltip="Export standard deviation maps to PhotoZ dat files."),
             sg.Checkbox('SNR Map', size=checkbox_size, key="SNR Map Export",
                            enable_events=True, default=gui.controller.is_export_snr_maps,
                            tooltip="Export SNR maps to PhotoZ dat files."),
             sg.Checkbox('MaxAmp Map', size=checkbox_size, key="Max Amp Map Export",
                            enable_events=True, default=gui.controller.is_export_max_amp_maps,
                            tooltip="Export max amplitude maps to PhotoZ dat files."),],
            [sg.Text("Export File Prefix:"), 
                sg.InputText(key="Export Trace Prefix",
                default_text=gui.controller.export_trace_prefix,
                enable_events=True,
                size=field_size,
                tooltip='Additional file prefix for exported trace files. Default will be <zda rec id>_<metric>.dat.'),
                sg.Checkbox('IDs Zero-Padded', size=(18, 1), key="IDs Zero-Padded", enable_events=True,
                            default=gui.controller.zero_pad_ids,
                            tooltip="When checked, zero-pad IDs in exported trace file names, e.g. 01_02_10roi.dat instead of 1_2_10roi.dat."),],
            [sg.Text("ROI Files:"), sg.Combo(gui.controller.roi_export_options,
                size=(12, 1),
                enable_events=True,
                default_value=gui.controller.roi_export_options[gui.controller.roi_export_idx],
                key='roi_export_options',
                tooltip='Options for selecting ROIs to export traces from the subdirectory containing the current zda file.' + \
                    ' If None, ROIs will not be changed during export.' + \
                    ' If Slice, ROIs will be selected by slice number and keyword in the ROIs file name.' + \
                    ' If Slice_Loc, ROIs will be selected by slice_location number and keyword in the ROIs file name.' + \
                    ' If Slice_Loc_Rec, ROIs will be selected by slice_location number, record number, and keyword in the ROIs file name.' ),
                sg.Text("Electrode:"), sg.Combo(gui.controller.electrode_export_options,
                size=(12, 1),
                enable_events=True,
                default_value=gui.controller.electrode_export_options[gui.controller.electrode_export_idx],
                key='electrode_export_options')],
            [sg.Text('ROIs Keyword:'), sg.InputText(key="ROIs Export Keyword",
                default_text=gui.controller.export_rois_keyword,
                enable_events=True,
                size=field_size,
                tooltip='Keyword to select ROI file names to export traces. Will also use <slice>, <loc>, ' + \
                    'and <rec> to identify ROIs per the selected drop-down option.'),
                sg.Text('  Electrode Keyword:'), sg.InputText(key="Electrode Export Keyword",
                                default_text=gui.controller.export_electrode_keyword,
                                enable_events=True,
                                size=field_size,
                                tooltip='Keyword to select electrode file names to export traces.'),],
            [sg.Text("Microns per pixel:"), 
             sg.InputText(key="Microns per Pixel",
                default_text=str(gui.controller.microns_per_pixel),
                enable_events=True,
                size=field_size,
                tooltip='Conversion factor for pixels to microns. Used in calculating distance to electrode. Old rig: 6.875 um/px. New rig: 6.0 um/px'),],
            [sg.Checkbox("Export by trial", size=checkbox_size, key="Export by trial",
                            enable_events=True, default=gui.controller.is_export_by_trial,
                            tooltip="When checked, export all data for each trial in addition to trial-averaged recordings."),
                            sg.Text("Number of Trials:"),
                            sg.InputText(key="Num Export Trials",
                                default_text=str(gui.controller.num_export_trials),
                                enable_events=True,
                                size=field_size,
                                tooltip='Number of trials to export data. Only used if exporting trials is enabled.'),],
            [sg.Button("Start Export", size=(13, 1), key="Start Export",),
             sg.Button("Regenerate Summary", size=(20, 1), key="Regenerate Summary",
                       tooltip="Attempt to regenerate the CSV summary file from current " + \
                        "settings and existing .dat files, without " + \
                        "re-doing the full export."),
                        sg.Button("PPR Wizard", size=(15, 1), key="PPR Wizard",
                        tooltip="Open the Paired Pulse Recording Wizard to guide through setting up PPR experiment export."),
                        sg.Button("ROI Wizard", size=(15, 1), key="ROI Wizard",
                        tooltip="Open the ROI Wizard to guide through setting up auto-generating ROIs for use with PhotoZ."),],
        ]
            
    def create_movie_maker_tab(self, gui):
        """ A tab with options for creating movies from exported data. 
            Option for start Pt and end Pt for movie creation. 
            Option for time interval between frames, in number of Pts. 
            Checkbox option to overwrite existing frames
            Button to start movie creation.
            """
        button_size = (15, 1)
        checkbox_size = (24, 1)
        field_size = (6, 1)
        return [
            [sg.Text("Movie Maker Options:")],
            [sg.Text("Start Pt:"), 
                sg.InputText(key="MM Start Pt",
                default_text=self.acqui_data.get_mm_start_pt(),
                enable_events=True,
                size=field_size,
                tooltip='Starting point for movie creation.')],
            [sg.Text("End Pt:"),
                sg.InputText(key="MM End Pt",
                default_text=self.acqui_data.get_mm_end_pt(),
                enable_events=True,
                size=field_size,
                tooltip='Ending point for movie creation.')],
            [sg.Text("Frame Interval (# Pts):"),
                sg.InputText(key="MM Frame Interval",
                default_text=self.acqui_data.get_mm_interval(),
                enable_events=True,
                size=field_size,
                tooltip='Number of points between frames in movie.')],
                [sg.Checkbox('Overwrite Existing Frames', size=checkbox_size, key="Overwrite Frames",
                             enable_events=True, default=self.acqui_data.get_mm_overwrite_frames(),
                             tooltip="When checked, overwrite existing frames in movie directory. " + \
                                "When unchecked, use existing frames (don't re-export)"),],

            [sg.Button("Start Movie Creation", size=button_size, key="Start Movie Creation",
                       tooltip="Create a movie from exported data.")],
        ]
        

    def create_left_column(self, gui):
        tab_group_basic = [sg.TabGroup([[
            sg.Tab('Recording Files', self.create_file_tab(gui)),
            sg.Tab('Auto Launcher', self.create_auto_tab(gui)),
            sg.Tab('Export Data', self.create_analysis_tab(gui)),
            sg.Tab('Movie Maker', self.create_movie_maker_tab(gui))
        ]])]
        return [tab_group_basic]

    def create_right_column(self, gui):
        tab_group_right = [sg.TabGroup([[
            sg.Tab('Trial Schedule', self.create_trials_tab(gui)),
            sg.Tab('Recording Settings', self.create_recording_settings_tab(gui)),
            sg.Tab('Specialized Recording', self.create_specialized_rec_tab(gui))
        ]])]
        return [tab_group_right]
