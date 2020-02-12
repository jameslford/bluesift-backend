VIKING_RANGE = 'https://www.vikingrange.com/consumer/products/tabs/subcategory_find_products_tab.jsp?id=cat12360038'
ARMSTRONG_RESIDENTIAL_ENGINEERED_TILE = 'https://www.armstrongflooring.com/residential/en-us/engineered-tile/_jcr_content.browseresults.json?pageSize=139&currPageIndex=1'
ARMSTRONG_RESIDENTIAL_HARDWOOD = 'https://www.armstrongflooring.com/residential/en-us/hardwood-flooring/_jcr_content.browseresults.json?pageSize=386&currPageIndex=1'
ARMSTRONG_RESIDENTIAL_LAMINATE = 'https://www.armstrongflooring.com/residential/en-us/laminate-flooring/_jcr_content.browseresults.json?pageSize=93&currPageIndex=1'
ARMSTRONG_RESIDENTIAL_LVT = 'https://www.armstrongflooring.com/residential/en-us/vinyl-flooring/luxury-vinyl-tile/_jcr_content.browseresults.json?pageSize=111&currPageIndex=1'
ARMSTRONG_RESIDENTIAL_RIGIDCORE = 'https://www.armstrongflooring.com/residential/en-us/rigid-core/_jcr_content.browseresults.json?pageSize=78&currPageIndex=1'
ARMSTRONG_RESIDENTIAL_VINYLSHEET = 'https://www.armstrongflooring.com/residential/en-us/vinyl-flooring/vinyl-sheet/_jcr_content.browseresults.json?pageSize=252&currPageIndex=1'
ARMSTRONG_RESIDENTIAL_VINYLTILE = 'https://www.armstrongflooring.com/residential/en-us/vinyl-flooring/vinyl-tile/_jcr_content.browseresults.json?pageSize=26&currPageIndex=1'
# ARMSTRONG_COMMERCIAL_HARDWOOD = 'https://www.armstrongflooring.com/commercial/en-us/products/commercial-hardwood/browse/_jcr_content.browseresults.json?category=hw&pageSize=60&currPageIndex=1'
ARMSTRONG_COMMERCIAL_HETEROVINYL = 'https://www.armstrongflooring.com/commercial/en-us/products/het/browse/_jcr_content.browseresults.json?category=het&pageSize=167&currPageIndex=1'
ARMSTRONG_COMMERCIAL_HOMOVINYL = 'https://www.armstrongflooring.com/commercial/en-us/products/hom/browse/_jcr_content.browseresults.json?category=hom&pageSize=89&currPageIndex=1'
ARMSTRONG_COMMERCIAL_LAMINATE = 'https://www.armstrongflooring.com/commercial/en-us/products/commercial-laminate/browse/_jcr_content.browseresults.json?category=lam&pageSize=27&currPageIndex=1'
ARMSTRONG_COMMERCIAL_LINOLEUM = 'https://www.armstrongflooring.com/commercial/en-us/products/linoleum/browse/_jcr_content.browseresults.json?category=lin&pageSize=92&currPageIndex=1'
ARMSTRONG_COMMERCIAL_LVT = 'https://www.armstrongflooring.com/commercial/en-us/products/lvt-luxury-flooring/browse/_jcr_content.browseresults.json?category=lvt&pageSize=320&currPageIndex=1'
ARMSTRONG_COMMERCIAL_VCT = 'https://www.armstrongflooring.com/commercial/en-us/products/vinyl-composition-tile/browse/_jcr_content.browseresults.json?category=vct&pageSize=386&currPageIndex=1'
ARMSTRONG_COMMERCIAL_RIGIDCORE = 'https://www.armstrongflooring.com/residential/en-us/rigid-core/_jcr_content.browseresults.json?pageSize=78&currPageIndex=1'
CROSSVILLE = 'https://www.crossvilleinc.com/api/Products'
SHAW_RESILIENT = '''https://shawfloors.com/api/odata/resilient?
            $top=81&$skip=0
            &$select=
            UniqueId,
            SellingStyleNbr,
            SellingColorNbr,
            SellingStyleName,
            SellingColorName,
            StaticRoomFlag,
            Vignette,
            ColorCount,
            MSRPRange,
            HasSwatchImage,
            SampleCount,
            IsMadeInUsa,
            SizeWidth,
            SizeLength,
            Thickness,
            Finish,
            Warranty,
            LightComWarranty,
            ProductCatDesc,
            Look,
            SurfaceTexture,
            GlossLevel,
            LightComWarranty,
            InstallationMethodDesc,
            CollectionDesc
            &$orderby=StyleSequence,UniqueId
            &$filter=(IsBaselineData%20eq%20false)%20and%20(IsDropped%20eq%20false)%20and%20(ColorCount%20gt%200)%20and%20(ProductGroupPermanentName%20eq%20%27shawfloors%27)%20and%20(HasMainImage%20eq%20true)%20and%20(ProductGroupShowOnBrowseCat%20eq%20true)%20and%20(HasMainImage%20eq%20true)%20and%20(StaticRoomFlag%20eq%20true%20or%20HasRenderImage%20eq%20true)
            &$count=true'''
SHAW_HARDWOOD = '''https://shawfloors.com/api/odata/Hardwoods?
            $top=81&$skip=0
            &$select=
            UniqueId,
            SellingStyleNbr,
            SellingColorNbr,
            SellingStyleName,
            SellingColorName,
            StaticRoomFlag,
            Vignette,
            ColorCount,
            MSRPRange,
            HasSwatchImage,
            SampleCount,
            IsMadeInUsa,
            InstallationType,
            PlankWidth,
            PlankLength,
            Thickness,
            EdgeType,
            GlossLevel,
            ColorVariationRatingShortDesc,
            Species,
            Warranty,
            Construction,
            CollectionDesc
            &$orderby=StyleSequence,UniqueId
            &$filter=(IsBaselineData%20eq%20false)%20and%20(IsDropped%20eq%20false)%20and%20(ColorCount%20gt%200)%20and%20(ProductGroupPermanentName%20eq%20%27shawfloors%27)%20and%20(HasMainImage%20eq%20true)%20and%20(ProductGroupShowOnBrowseCat%20eq%20true)%20and%20(HasMainImage%20eq%20true)%20and%20(StaticRoomFlag%20eq%20true%20or%20HasRenderImage%20eq%20true)
            &$count=true'''
SHAW_LAMINATE = '''https://shawfloors.com/api/odata/Laminates?
            $top=1000
            &$select=
            UniqueId,
            SellingStyleNbr,
            SellingColorNbr,
            PlankWidth,
            InstallationType,
            PlankLength,
            Thickness,
            Warranty,
            EdgeType,
            SellingStyleName,
            SellingColorName,
            StaticRoomFlag,
            Vignette,
            ColorCount,
            MSRPRange,
            HasSwatchImage,
            SampleCount,
            IsMadeInUsa,
            CollectionDesc
            &$filter=(IsBaselineData%20eq%20false)%20and%20(IsDropped%20eq%20false)%20and%20(ColorCount%20gt%200)%20and%20(ProductGroupPermanentName%20eq%20%27shawfloors%27)%20and%20(HasMainImage%20eq%20true)%20and%20(ProductGroupShowOnBrowseCat%20eq%20true)%20and%20(HasMainImage%20eq%20true)%20and%20(StaticRoomFlag%20eq%20true%20or%20HasRenderImage%20eq%20true)
            &$orderby=StyleSequence,UniqueId
            &$count=true'''
SHAW_TILE = '''https://shawfloors.com/api/odata/Ceramics?
            $top=1000
            &$select=
            UniqueId,
            SellingStyleNbr,
            SellingColorNbr,
            SellingStyleName,
            SellingColorName,
            StaticRoomFlag,
            Thickness,
            Thickness,
            WIDTH,
            LengthDimension,
            InstallOnFloorsAndWalls,
            InstallOnFloors,
            InstallOnWalls,
            InstallOnExterior,
            InstallOnCountertops,
            Look,
            CeramicConstruction,
            SurfaceTexture,
            SurfaceFinish,
            WetCof,
            Vignette,
            ColorCount,
            MSRPRange,
            SampleCount,
            MadeInUSA
            &$filter=(IsBaselineData%20eq%20false)%20and%20(IsDropped%20eq%20false)%20and%20(ColorCount%20gt%200)%20and%20(ProductGroupPermanentName%20eq%20%27shawfloors%27)%20and%20(HasMainImage%20eq%20true)%20and%20(ProductGroupShowOnBrowseCat%20eq%20true)%20and%20(HasMainImage%20eq%20true)%20and%20(StaticRoomFlag%20eq%201%20or%20HasRenderImage%20eq%20true)
            &$orderby=StyleSequence,UniqueId
            &$count=true'''