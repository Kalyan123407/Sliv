#!/data/data/com.termux/files/usr/bin/bash

echo "🚀 Auto Runner Started!"

while true; do
    echo ""
    echo "⏰ $(date '+%Y-%m-%d %H:%M:%S') - Cycle Start"

    # Step 1: Python script chalao
    echo "🐍 sony.py run ho raha hai..."
    python sony.py
    echo "✅ sony.py complete!"

    # Step 2: Git add + commit + push
    echo "📤 Git push ho raha hai..."
    git add .
    git commit -m "🔄 Auto update $(date '+%Y-%m-%d %H:%M:%S')"
    git branch -M main
    git push -u origin main --force
    echo "✅ GitHub push done!"

    # Step 3: 11 ghante wait
    echo "😴 Next cycle 11 ghante baad..."
    echo "⏰ Agli run: $(date -d '+11 hours' '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -v+11H '+%Y-%m-%d %H:%M:%S')"
    sleep 39600

done

