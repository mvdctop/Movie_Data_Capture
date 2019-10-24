# The video format you want to move.
$videoFormatLists=("mp4","wmv")
# Source video directory
$fromDir="X:\av"
# Target video directory(path to AVData)
$toDir="X:\AVData"

function moveVideos ($fromDir, $toDir,$videoFormat) {
    $list=@(Get-ChildItem -Path $fromDir -Recurse -File -Include "*.$videoFormat" |  ForEach-Object {$_.FullName})
    $list.Length

    # Only one video to move.
    if ($list.Length -eq 1) {
        Move-Item $list.Replace("`[","``[").Replace("`]","``]") $toDir
    # More than one videos to move.
    } else {
        for($idx=0; $idx -lt $list.Length; $idx++) {
            echo "Move file $list[$idx].Replace("`[","``[").Replace("`]","``]") to $toDir"
            # escapse [ ]
            Move-Item $list[$idx].Replace("`[","``[").Replace("`]","``]") $toDir
        }
    }
}

# Move videos
for($idy=0; $idy -lt $videoFormatLists.Length; $idy++) {
       moveVideos $fromDir $toDir $videoFormatLists[$idy]
}

