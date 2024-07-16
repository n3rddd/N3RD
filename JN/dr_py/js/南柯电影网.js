Object.assign(muban.mxpro.二级, {
    tab_text: 'div--small&&Text',
});
var rule = {
  模板: 'mxpro',
  title: "南柯电影网",
  host: "https://nkdyw.cc",
  url: "/show/fyclassfyfilter.html",
  searchUrl: "/dy/**----------fypage---.html",
  searchable: 2,
  quickSearch: 0,
  filterable: 1,
  filter: "H4sIAAAAAAAAA+1Y204bMRD9l33mwRuu5VcqHlAVqagtlQqtVCGkIggKJCG9pKSUOzQQ2gALiQgJkPxMvMn+RZ3semYWtbZFb0jdt5wz3onPrL1n7BnLtkYfzlhP4q+tUYtvODxdt/qsyfFncYpfjT99Ge8NnOzSiaI3X+zSAlizfT7bujzm6zf8y6G3thjEQlR4nHew5l6ehsYF1K18WcetNcL5fCo8zm2UvXwxNC6g5Lh2Y0WQwYgAyJibL7gbpSAWABnzto/wuQDIWCd1hrEAQM7yR4wFAGMOjTk0xhtVjAUAtDYX2jd5dxUKBxieXt5xU01RcpkAMOS4XnY38jKBD6BG77Z44lLWyAeQuVrpFJoyrQ/wHdS8+gFUvwfguYzDIRYAqMNCVkyNJ49kKQBDhQvNdva4vbQmiwwYcjTK/jOt+meZhlIw7jQnGDd/IQcBhpnuFUV6/qEgJwsYZpOp8oQjp+IDfKd7GAsArev+N1JXASCWPONODh9FDCvwU9PdqfGrqlyEgEmVxErBEnUBxLLnvJHiJ3ITIYaZp7/y4pycuQ+gJoVC9ysAbwgx7oFsZy4He6AHILZcIvXyAfzrqiMWJ9/clX8MWI64/YXh6aR48WQugCFn95WkZEIf4DrMe5tbsA57AGKJC34yL2M+mB3rRoMPY63SurohH0aJTT6MMRYbCLjeT8L3I99P+RjyMcrbyNuUZ8gzwtsPgBc/CT+C/Ajlh5EfpvwQ8kOUH0R+kPKo16Z6bdRrU7026rWpXhv12lSvjXptqpehXkb1MtTLqF6GehnVy1Avo3oZ6mVUL0O9jOplqJdRvQz1MqqXoV5G9TLUK37ShemuvOf1LC5MwOGFKb5yXr6CQUFNT4gH4Ptdr7tOLhR/PDE9hfv4dIEnF0PxqUfPX8S7cxnrs2JRD/GneghFn6B1egPvVPQoqj7E2HO133h9B6DqH/SOrexa9N3UxnbnTVkYgkwA2KRjUnVFetdX9RMqxxY17tYAHwVs4oT6LknfT3hHJXezIP4UV0eIMu9rWleFztI5T0K7CtikIxProHV9IBTgPEJU5PCRw0cOb+Tw/f+Lw6ucWuX+ShdXdAZ6F1d6tMLd7nrHYOrtynO91vf1vYne2w38W+cAxl2Iyo2Fb4lDrwcHT8QmnYDe45Qn18wu382J1gHCEsOIn5/gI/+L/C/yPxP/G/g3/mfqa6Y+qfc/lVfd2f9UN+GlQ5FJxnxg7o0qt/4dHqd3Kb0H6U9U+rOgyj9+zbt4Zs/dP+E70qkRm/uw6jSqugFu1dI8kcIwYsjcu8IV1XQr663rt7fvdkMBmO+P7nJlTHuDrDpPmp5rlX5t2JEobh4i145cO3JtE9ce/GuuHe3JaE9Ge9JkTw6RPXk/ZjR8z2Y0+x3RVvC8lSMAAA==",
  filter_url: "-{{fl.地区}}-{{fl.排序}}------fypage---{{fl.年份}}",
  filter_def: {},
  headers: {
    "User-Agent": "MOBILE_UA"
  },
  timeout: 5000,
  class_parse: ".navbar-items&&li;a&&Text;a&&href;(\\d+)",
  cate_exclude: "",
  tab_exclude:"排序",
  play_parse: true,
  lazy:$js.toString(()=>{
    input = {parse:1,url:input,js:''};
  }),
  double: true,
}