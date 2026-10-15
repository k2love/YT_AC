import json

# Test recursive cleaner
test_data = {
    "contents": {
        "tvBrowseRenderer": {
            "content": {
                "tvSurfaceContentRenderer": {
                    "content": {
                        "sectionListRenderer": {
                            "contents": [
                                {
                                    "adSlotRenderer": {
                                        "adSlotType": "SLOT_TYPE_MASTHEAD",
                                        "title": "대문짝만한 스폰서 광고"
                                    }
                                },
                                {
                                    "shelfRenderer": {
                                        "title": "정상 추천 영상",
                                        "items": [
                                            {"videoRenderer": {"title": "정상 영상 1"}},
                                            {"inFeedAdRenderer": {"title": "광고 스폰서 영상"}},
                                            {"videoRenderer": {"title": "정상 영상 2"}},
                                            {"promotedVideoRenderer": {"title": "프로모션 광고 영상"}}
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    },
    "adPlacements": [{"ad": 1}],
    "adSlots": [{"slot": 2}],
    "playerAds": [{"ad": 3}]
}

def clean_ads(obj):
    ad_keys = {
        "adslotrenderer", "infeedadrenderer", "mastheadadrenderer", "mastheadrenderer",
        "heroadrenderer", "promotedvideorenderer", "promotedsparkleswebrenderer",
        "statementbannerrenderer", "bannerpromorenderer", "adbreakservicerenderer",
        "adplacements", "adslots", "playerads", "adbreakheartbeatparams"
    }
    
    if isinstance(obj, dict):
        keys_to_del = [k for k in obj.keys() if k.lower() in ad_keys]
        for k in keys_to_del:
            del obj[k]
        for k, v in list(obj.items()):
            clean_ads(v)
    elif isinstance(obj, list):
        i = len(obj) - 1
        while i >= 0:
            item = obj[i]
            if isinstance(item, dict):
                has_ad = any(k.lower() in ad_keys for k in item.keys())
                if has_ad:
                    del obj[i]
                    i -= 1
                    continue
            clean_ads(item)
            i -= 1

print("Before cleaning:", json.dumps(test_data, ensure_ascii=False, indent=2))
clean_ads(test_data)
print("\nAfter cleaning:", json.dumps(test_data, ensure_ascii=False, indent=2))
