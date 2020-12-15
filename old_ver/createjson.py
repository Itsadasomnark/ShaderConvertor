import json

data = {
	"renderer" : [
		"arnold",
		"vray"
	],
	"aiStandardSurface":{
		"aiStandardSurface":["VRayMtl"],
		"base":["diffuseColorAmount"],
		"baseColor":["diffuseColor"],
		"baseColorR":["diffuseColorR"],
		"baseColorG":["diffuseColorG"],
		"baseColorB":["diffuseColorB"],
		"diffuseRoughness":["roughnessAmount"],
		"specular":["reflectionColorAmount"],
		"specularColor":["reflectionColor"],
		"specularColorR":["reflectionColorR"],
		"specularColorG":["reflectionColorG"],
		"specularColorB":["reflectionColorB"],
		"specularRoughness":["reflectionGlossiness","Inverse"],
		"metalness":["metalness"],
		"transmission":["refractionColorAmount"],
		"transmissionColor":["refractionColor"],
		"transmissionColorR":["refractionColorR"],
		"transmissionColorG":["refractionColorG"],
		"transmissionColorB":["refractionColorB"]
		},   
	"aiLayerShader":{
		"aiLayerShader":["VRayBlendMtl"],
		"input1":["base_material"],
		"input2":["coat_material_0"]
		}
	}
with open('C:/Users/bossd/Desktop/Thesis/script/config/arnold.json', 'w') as jsonfile:
    json.dump(data, jsonfile)