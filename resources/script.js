// Define main function (script entry)

function main(config, profileName) {
  return config;
}

function main(config) {
  // 1. 定义关键词与 Emoji 的对应关系
  const emojiMap = {
    "香港": "🇭🇰",
    "HK": "🇭🇰",
    "Hong Kong": "🇭🇰",
    "台湾": "🇹🇼",
    "TW": "🇹🇼",
    "Taiwan": "🇹🇼",
    "美国": "🇺🇸",
    "US": "🇺🇸",
    "USA": "🇺🇸",
    "日本": "🇯🇵",
    "JP": "🇯🇵",
    "Japan": "🇯🇵",
    "新加坡": "🇸🇬",
    "SG": "🇸🇬",
    "Singapore": "🇸🇬",
    "韩国": "🇰🇷",
    "KR": "🇰🇷",
    "Korea": "🇰🇷",
    "英国": "🇬🇧",
    "UK": "🇬🇧",
    "专属": "✅"
  };

  // 记录旧名称到新名称的映射，用于同步修改策略组
  const nameMapping = {};

  // 2. 遍历并修改所有节点名称
  if (config.proxies) {
    config.proxies.forEach(proxy => {
      const oldName = proxy.name;
      for (const [key, emoji] of Object.entries(emojiMap)) {
        // 如果节点名包含关键词且还没加过该 emoji
        if (oldName.toLowerCase().includes(key.toLowerCase()) && !oldName.includes(emoji)) {
          proxy.name = `${emoji} ${oldName}`;
          nameMapping[oldName] = proxy.name;
          break; // 匹配到一个就跳出，防止重复添加
        }
      }
    });
  }

  // 3. 同步修改策略组（proxy-groups）中的节点引用
  // 这步非常关键，否则策略组会因为找不到原节点名而报错
  if (config['proxy-groups']) {
    config['proxy-groups'].forEach(group => {
      if (group.proxies) {
        group.proxies = group.proxies.map(name => nameMapping[name] || name);
      }
    });
  }

  return config;
}