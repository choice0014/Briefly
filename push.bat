@echo off
:: UTF-8로 코드페이지 변경 (한글 깨짐 방지)
chcp 65001 > nul

echo ========================================
echo  GitHub 코드 업로드 자동화 스크립트
echo ========================================

:: Git 초기화 (이미 되어 있으면 건너뜀)
if not exist .git (
    echo [1/4] Git 저장소 초기화 중...
    git init
    git remote add origin https://github.com/choice0014/Briefly.git
    git branch -M main
)

echo [2/4] 변경된 파일 추가 중...
git add .

echo [3/4] 커밋 메시지 작성 중...
set /p msg="커밋 메시지를 입력하세요 (기본값: Update): "
if "%msg%"=="" set msg=Update

git commit -m "%msg%"

echo [4/4] GitHub로 업로드 중...
git push -u origin main

echo ========================================
echo  업로드가 완료되었습니다!
echo ========================================
pause
